
import asyncio
from datetime import datetime, timezone

from fastapi import FastAPI
from contextlib import asynccontextmanager
from models import ApiKey
from sqlmodel import select
from app.logging_config import logger
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from .rate_limit_config import limiter
from db import create_all_tables, SessionLocal, engine
from .routers import shortener
from app.services.apikey_services import generate_api_key


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
        with SessionLocal(engine) as session:
            key = session.exec(select(ApiKey).order_by(
                ApiKey.created_at.desc())).first()  # type: ignore
            if not key or not key.expires_at:
                logger.info("No valid API key found, generating a new one.")
                generate_api_key(session)
            else:
                expires_at = key.expires_at
                # Si está sin tz, se la fijamos
                if expires_at.tzinfo is None:
                    expires_at = expires_at.replace(tzinfo=timezone.utc)
                if expires_at < datetime.now(timezone.utc):
                    generate_api_key(session)

        await asyncio.sleep(60 * 60 * 24)  # 24 hours
