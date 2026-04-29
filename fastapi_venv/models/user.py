from pydantic import BaseModel, Field
from database.todos import Base
from sqlalchemy import Column, Integer, String, Boolean,Numeric
from passlib.context import CryptContext

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRequest(BaseModel):
    id: int = Field(default=None, description="ID of the user",PrimaryKeyConstraint=True)
    email: str = Field(min_length=5, max_length=100, description="Email address of the user")
    password: str = Field(min_length=8, max_length=100, description="Password for the user")
    is_active: bool = Field(default=True, description="Active status of the user")
    first_name: str = Field(min_length=1, max_length=50, description="First name of the user")
    last_name: str = Field(min_length=1, max_length=50, description="Last name of the user")

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "johndoe@example.com",
                "password": "securepassword123",
                "is_active": True,
                "first_name": "John",
                "last_name": "Doe"
            }
        }
    }


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True,autoincrement=True)
    username = Column(String(50), index=True)
    email = Column(String(100), index=True, unique=True ,nullable=False)
    password = Column(String(255))
    is_active = Column(Boolean, default=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
