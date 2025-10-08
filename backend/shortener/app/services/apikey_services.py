
import hashlib

from fastapi import HTTPException, status
from db import SessionDep
from sqlmodel import select
from app.logging_config import logger
from models import ApiKey, CreateApiKey


# Generate Api Key


def generate_api_key(payload: CreateApiKey, session: SessionDep):
    api_key_old = payload.old_api_key
    api_key_new = payload.api_key

    def _hash_key(api_key: str) -> str:
        return hashlib.sha256(api_key.encode()).hexdigest()

    if not api_key_old:
        existing_key = session.exec(select(ApiKey)).first()
        if existing_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unauthorized. API key already exists.",
            )

    else:
        old_key_hashed = _hash_key(api_key_old)
        key_record = session.exec(
            select(ApiKey).where(ApiKey.key_hash == old_key_hashed)
        ).first()
        if not key_record:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized access. Invalid old API key.",
            )

    new_key_hashed = _hash_key(api_key_new)
    new_key_record = ApiKey(key_hash=new_key_hashed)

    session.add(new_key_record)
    session.commit()
    session.refresh(new_key_record)

    logger.info(f"New API Key generated: {api_key_new[:4]}****")

    return api_key_new


# Validate Api key


def validate_api_key(session: SessionDep, api_key: str) -> None:
    hashed = hashlib.sha256(api_key.encode()).hexdigest()
    key = session.exec(select(ApiKey).where(ApiKey.key_hash == hashed)).first()
    if not key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key."
        )
    logger.info(f"API key validated (prefix={api_key[:4]}****)")
