
from fastapi import FastAPI
from contextlib import asynccontextmanager
from db import create_all_tables
from .routers import shortener


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_all_tables(app)
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(shortener.router)
