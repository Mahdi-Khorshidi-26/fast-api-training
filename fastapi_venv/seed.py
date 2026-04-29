from sqlalchemy import func, text

from database.todos import SessionLocal, create_db
from models.todos import Todos
from models.user import User, bcrypt_context


TARGET_USER_COUNT = 4
TARGET_ROW_COUNT = 20

SEED_USERS = [
    {
        "username": "johndoe",
        "email": "john@example.com",
        "password": "securepassword123",
        "is_active": True,
        "first_name": "John",
        "last_name": "Doe",
    },
    {
        "username": "janesmith",
        "email": "jane@example.com",
        "password": "securepassword123",
        "is_active": True,
        "first_name": "Jane",
        "last_name": "Smith",
    },
    {
        "username": "alexrivera",
        "email": "alex@example.com",
        "password": "securepassword123",
        "is_active": True,
        "first_name": "Alex",
        "last_name": "Rivera",
    },
    {
        "username": "samlee",
        "email": "sam@example.com",
        "password": "securepassword123",
        "is_active": True,
        "first_name": "Sam",
        "last_name": "Lee",
    },
]

SEED_TODOS = [
    {
        "title": "Plan weekly meals",
        "description": "Choose simple dinners and write the shopping list",
        "completed": False,
    },
    {
        "title": "Review API routes",
        "description": "Check todo endpoints and response status codes",
        "completed": True,
    },
    {
        "title": "Clean workspace",
        "description": "Organize desk, cables, notebooks, and charger",
        "completed": False,
    },
    {
        "title": "Read SQLAlchemy docs",
        "description": "Review sessions, commits, rollbacks, and queries",
        "completed": False,
    },
    {
        "title": "Write project notes",
        "description": "Summarize current FastAPI setup and next steps",
        "completed": True,
    },
    {
        "title": "Back up database",
        "description": "Export important local data before schema changes",
        "completed": False,
    },
    {
        "title": "Test create todo",
        "description": "Send a POST request and verify the saved record",
        "completed": True,
    },
    {
        "title": "Test update todo",
        "description": "Send a PUT request and confirm the row changes",
        "completed": False,
    },
    {
        "title": "Test delete todo",
        "description": "Delete one test record and verify the response",
        "completed": False,
    },
    {
        "title": "Improve validation",
        "description": "Review title and description field limits",
        "completed": False,
    },
    {
        "title": "Add API tags",
        "description": "Group todo endpoints in the OpenAPI docs",
        "completed": False,
    },
    {
        "title": "Check database indexes",
        "description": "Confirm useful indexes exist for todo lookups",
        "completed": True,
    },
    {
        "title": "Create README",
        "description": "Document setup, run commands, and seed command",
        "completed": False,
    },
    {
        "title": "Pin dependencies",
        "description": "Save installed packages into requirements file",
        "completed": False,
    },
    {
        "title": "Add health endpoint",
        "description": "Create a simple endpoint to confirm app status",
        "completed": False,
    },
    {
        "title": "Review error messages",
        "description": "Make not found responses clear and consistent",
        "completed": True,
    },
    {
        "title": "Try pagination",
        "description": "Call list endpoint with skip and limit values",
        "completed": False,
    },
    {
        "title": "Check Oracle connection",
        "description": "Verify database host, service name, and credentials",
        "completed": True,
    },
    {
        "title": "Add tests",
        "description": "Write basic tests for todo CRUD behavior",
        "completed": False,
    },
    {
        "title": "Run Uvicorn",
        "description": "Start the FastAPI app and open Swagger UI",
        "completed": False,
    },
]


def ensure_todos_owner_id_column(db) -> None:
    owner_id_exists = db.execute(
        text(
            """
            SELECT COUNT(*)
            FROM user_tab_columns
            WHERE table_name = 'TODOS'
              AND column_name = 'OWNER_ID'
            """
        )
    ).scalar()

    if owner_id_exists:
        return

    db.execute(text("ALTER TABLE todos ADD (owner_id INTEGER)"))
    print("Added missing owner_id column to todos.")


def seed_users(db, target_count: int = TARGET_USER_COUNT) -> list[int]:
    seed_emails = [user["email"] for user in SEED_USERS[:target_count]]
    existing_users = db.query(User).filter(User.email.in_(seed_emails)).order_by(User.id).all()
    existing_emails = {user.email for user in existing_users}

    max_id = db.query(func.max(User.id)).scalar() or 0
    users_to_create = []

    for user_data in SEED_USERS[:target_count]:
        if user_data["email"] in existing_emails:
            continue

        data = user_data.copy()
        data["password"] = bcrypt_context.hash(data["password"])
        users_to_create.append(User(id=max_id + len(users_to_create) + 1, **data))

    if users_to_create:
        db.add_all(users_to_create)
        db.flush()

    users = existing_users + users_to_create
    print(f"Seed users ready: {len(users)}.")
    return [user.id for user in users]


def seed_todos(db, owner_ids: list[int], target_count: int = TARGET_ROW_COUNT) -> int:
    existing_count = db.query(func.count(Todos.id)).scalar() or 0
    rows_to_create = max(target_count - existing_count, 0)

    if rows_to_create == 0:
        print(f"Todos table already has {existing_count} rows.")
        return 0

    max_id = db.query(func.max(Todos.id)).scalar() or 0
    todos = []

    for index, todo_data in enumerate(SEED_TODOS[:rows_to_create], start=1):
        owner_id = owner_ids[(existing_count + index - 1) % len(owner_ids)]
        todos.append(Todos(id=max_id + index, owner_id=owner_id, **todo_data))

    db.add_all(todos)
    db.flush()

    print(f"Inserted {len(todos)} todos. Total rows: {existing_count + len(todos)}.")
    return len(todos)


def assign_todo_owners(db, owner_ids: list[int]) -> int:
    todos_without_owner = db.query(Todos).filter(Todos.owner_id.is_(None)).order_by(Todos.id).all()

    for index, todo in enumerate(todos_without_owner):
        todo.owner_id = owner_ids[index % len(owner_ids)]

    print(f"Assigned owners to {len(todos_without_owner)} existing todos.")
    return len(todos_without_owner)


def seed_database() -> None:
    create_db()

    db = SessionLocal()
    try:
        ensure_todos_owner_id_column(db)

        owner_ids = seed_users(db)
        if not owner_ids:
            raise RuntimeError("No users available to assign as todo owners.")

        seed_todos(db, owner_ids)
        assign_todo_owners(db, owner_ids)
        db.commit()
        print("Seed completed.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
