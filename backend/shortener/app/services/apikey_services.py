
import uuid
import hashlib

from fastapi import HTTPException, status
from db import SessionDep
from sqlmodel import select
from datetime import datetime, timezone, timedelta
from logging_config import logger
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
    if key.expires_at and key.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key has expired.")
    logger.info(f"API key {key.id} validated successfully")
