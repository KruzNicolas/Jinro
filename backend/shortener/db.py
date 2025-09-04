
from fastapi import FastAPI, Depends
from sqlmodel import SQLModel, Session, create_engine
from typing import Annotated

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("POSTGRE_URL")

if not DATABASE_URL:
    raise ValueError(
        "No DATABASE_URL set for the application. Did you forget to set it?")

engine = create_engine(DATABASE_URL, echo=True)


def create_all_tables(app):
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
