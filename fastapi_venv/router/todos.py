from fastapi import APIRouter, HTTPException, status, Query, Path
from database.todos import db_dependency
from models.todos import TodoRequest, Todos
router_todos = APIRouter()
    


@router_todos.get("/todos", status_code=status.HTTP_200_OK)
def read_todos(
    db: db_dependency,
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=10, ge=1, le=100, description="Max number of records to return"),
):
    todos = db.query(Todos).offset(skip).limit(limit).all()
    if not todos:
        raise HTTPException(status_code=404, detail="No todos found")
    return todos

@router_todos.post("/todos")
def create_todo(todo: TodoRequest, db: db_dependency):
    db_todo = Todos(**todo.model_dump())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@router_todos.delete("/todos/{todo_id}", status_code=status.HTTP_200_OK)
def delete_todo(
    db: db_dependency,
    todo_id: int = Path(gt=0, description="ID of the todo to delete"),
):
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
    return {"message": "Todo deleted successfully"}

@router_todos.put("/todos/{todo_id}", status_code=status.HTTP_200_OK)
def update_todo(
    updated_todo: TodoRequest,
    db: db_dependency,
    todo_id: int = Path(gt=0, description="ID of the todo to update"),
):
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo.title = updated_todo.title
    todo.description = updated_todo.description
    todo.completed = updated_todo.completed
    db.add(todo) 
    db.commit()
    db.refresh(todo)
    return todo

@router_todos.get("/todos/{todo_id}", status_code=status.HTTP_200_OK)
def read_todo(
    db: db_dependency,
    todo_id: int = Path(gt=0, description="ID of the todo to retrieve"),
):
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo