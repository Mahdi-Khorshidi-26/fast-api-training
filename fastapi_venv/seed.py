from sqlalchemy import func

from database.todos import SessionLocal, create_db
from models.todos import Todos


TARGET_ROW_COUNT = 20

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


def seed_todos(target_count: int = TARGET_ROW_COUNT) -> int:
    create_db()

    db = SessionLocal()
    try:
        existing_count = db.query(func.count(Todos.id)).scalar() or 0
        rows_to_create = max(target_count - existing_count, 0)

        if rows_to_create == 0:
            print(f"Todos table already has {existing_count} rows.")
            return 0

        max_id = db.query(func.max(Todos.id)).scalar() or 0
        todos = []

        for index, todo_data in enumerate(SEED_TODOS[:rows_to_create], start=1):
            todos.append(Todos(id=max_id + index, **todo_data))

        db.add_all(todos)
        db.commit()

        print(f"Inserted {len(todos)} todos. Total rows: {existing_count + len(todos)}.")
        return len(todos)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_todos()
