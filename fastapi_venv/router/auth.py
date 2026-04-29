from fastapi import APIRouter, HTTPException, status, Query, Path
from database.todos import db_dependency
from models.user import User, UserRequest, bcrypt_context
router_users = APIRouter()

@router_users.get("/auth", status_code=status.HTTP_200_OK)
def read_users(
    db: db_dependency,
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=10, ge=1, le=100, description="Max number of records to return"),
):
    users = db.query(User).offset(skip).limit(limit).all()
    if not users:
        raise HTTPException(status_code=404, detail="No users found")
    return users


@router_users.post("/auth")
def create_user(user: UserRequest, db: db_dependency):
    user_data = user.model_dump()
    user_data["password"] = bcrypt_context.hash(user.password)
    db_user = User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router_users.delete("/auth/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(
    db: db_dependency,
    user_id: int = Path(gt=0, description="ID of the user to delete"),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

@router_users.get("/auth/{user_id}", status_code=status.HTTP_200_OK)
def read_user(
    db: db_dependency,
    user_id: int = Path(gt=0, description="ID of the user to retrieve"),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router_users.put("/auth/{user_id}", status_code=status.HTTP_200_OK)
def update_user(
    updated_user: UserRequest,
    db: db_dependency,
    user_id: int = Path(gt=0, description="ID of the user to update"),  
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.email = updated_user.email
    user.password = bcrypt_context.hash(updated_user.password)
    user.is_active = updated_user.is_active
    user.first_name = updated_user.first_name
    user.last_name = updated_user.last_name
    db.add(user) 
    db.commit()
    db.refresh(user)
    return user
