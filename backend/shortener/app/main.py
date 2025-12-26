
from fastapi import FastAPI
from contextlib import asynccontextmanager
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from .rate_limit_config import limiter
from db import create_all_tables, SessionLocal, engine
from .routers import shortener


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_all_tables(app)
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(shortener.router)
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore
