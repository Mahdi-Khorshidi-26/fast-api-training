from sqlalchemy import Column, Integer, String, Boolean,ForeignKey
from pydantic import BaseModel, Field
from database.todos import Base


class TodoRequest(BaseModel):
    title: str = Field(min_length=3, max_length=50, description="Title of the todo")
    description: str = Field(min_length=3, max_length=200, description="Description of the todo")
    completed: bool = Field(default=False, description="Completion status")

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Buy groceries",
                "description": "Milk, Bread, Eggs",
                "completed": False
            }
        }
    }


class Todos(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    completed = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"), index=True)  # Optional: link to user who created the todo
