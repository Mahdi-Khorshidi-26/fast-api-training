from fastapi import FastAPI

from database.todos import create_db
from router.todos import router_todos
from router.auth import router_users

app = FastAPI()
app.include_router(router_todos)
app.include_router(router_users)
create_db()