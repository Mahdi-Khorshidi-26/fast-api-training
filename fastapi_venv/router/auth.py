from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from database.todos import db_dependency, form_data
from models.user import User, UserRequest, bcrypt_context
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from models.token import Token
from typing import Annotated

router_users = APIRouter(
    prefix="/auth",
    tags=["users"],
)

secrete_key = "7a4bed894125ed8709a11232537dee6cfba92c7d31780ff8d5ce8fc5d9ae2779"
algorithm = "HS256"


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
token_type = Annotated[str, Depends(oauth2_scheme)]


def get_current_user(token: token_type, db: db_dependency):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, secrete_key, algorithms=[algorithm])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        if username is None or user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user


user_dependency = Annotated[dict, Depends(get_current_user)]


def create_access_token(username: str, user_id:int, expires_delta: timedelta):
    to_encode = {"sub": username, "user_id": user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expires})
    encoded_jwt = jwt.encode(to_encode, secrete_key, algorithm=algorithm)
    return encoded_jwt



@router_users.get("/", status_code=status.HTTP_200_OK)
def read_users(
    db: db_dependency,
    current_user: user_dependency,
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=10, ge=1, le=100, description="Max number of records to return"),
):
    
    users = db.query(User).offset(skip).limit(limit).all()
    if not users:
        raise HTTPException(status_code=404, detail="No users found")
    return users


@router_users.post("/")
def create_user(user: UserRequest, db: db_dependency):
    user_data = user.model_dump()
    user_data["password"] = bcrypt_context.hash(user.password)
    db_user = User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router_users.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(
    db: db_dependency,
    current_user: user_dependency,
    user_id: int = Path(gt=0, description="ID of the user to delete"),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

@router_users.get("/{user_id}", status_code=status.HTTP_200_OK)
def read_user(
    db: db_dependency,
    current_user: user_dependency,
    user_id: int = Path(gt=0, description="ID of the user to retrieve"),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router_users.put("/{user_id}", status_code=status.HTTP_200_OK)
def update_user(
    updated_user: UserRequest,
    db: db_dependency,
    current_user: user_dependency,
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


@router_users.post("/login", status_code=status.HTTP_200_OK,response_model=Token)
def login(form_data: form_data, db: db_dependency):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not bcrypt_context.verify(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(
        username=user.email, user_id=user.id, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}