
import uuid
import hashlib

from fastapi import HTTPException, status
from db import SessionDep
from sqlmodel import select
from datetime import datetime, timezone, timedelta
from app.logging_config import logger
from models import ApiKey


# Generate Api Key


def generate_api_key(session: SessionDep):
    raw_key = uuid.uuid4().hex + uuid.uuid4().hex
    hashed_key = hashlib.sha256(raw_key.encode()).hexdigest()
    expires = datetime.now(timezone.utc) + timedelta(weeks=1)

    new_key = ApiKey(key_hash=hashed_key, expires_at=expires)
    session.add(new_key)
    session.commit()
    logger.info(f"New API Key valid until {expires.isoformat()}: {raw_key}")
    return raw_key

# Validate Api key


def validate_api_key(session: SessionDep, api_key: str) -> None:
    hashed = hashlib.sha256(api_key.encode()).hexdigest()
    key = session.exec(select(ApiKey).where(ApiKey.key_hash == hashed)).first()
    if not key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key.")

    now = datetime.now(timezone.utc)
    expires_at = key.expires_at
    if expires_at:
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if expires_at < now:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="API Key has expired."
            )

    logger.info(f"API key {key.id} validated successfully")
