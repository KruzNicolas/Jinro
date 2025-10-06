
import asyncio
from datetime import datetime, timezone

from fastapi import FastAPI
from contextlib import asynccontextmanager
from models import ApiKey
from sqlmodel import select
from logging_config import logger
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from db import create_all_tables, SessionLocal, engine
from .routers import shortener
from services.apikey_services import generate_api_key

limiter = Limiter(key_func=get_remote_address, default_limits=["50/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_all_tables(app)
    asyncio.create_task(key_rotation_scheduler())
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(shortener.router)
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore


async def key_rotation_scheduler():
    while True:
        await asyncio.sleep(60 * 60 * 24)  # 24 hours
        with SessionLocal(engine) as session:
            key = session.exec(select(ApiKey).order_by(
                ApiKey.created_at.desc())).first()  # type: ignore
            if not key or not key.expires_at or key.expires_at < datetime.now(timezone.utc):
                logger.info("No valid API key found, generating a new one.")
                generate_api_key(session)
