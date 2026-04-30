from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from fastapi.security import OAuth2PasswordRequestForm
# SQLALCHEMY_DATABASE_URL = (
#     "oracle+oracledb://mahdi:mahdi@172.16.60.66:1521/?service_name=orcl"
# )

SQLALCHEMY_DATABASE_URL = "sqlite:///./todos.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def create_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
form_data = Annotated[OAuth2PasswordRequestForm, Depends()]