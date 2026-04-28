from fastapi import FastAPI

from database.todos import create_db
from router.todos import router_todos

app = FastAPI()
app.include_router(router_todos)
create_db()