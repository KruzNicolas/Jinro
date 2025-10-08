
# Standard library imports

import os
import re
import httpx
from datetime import datetime, timezone

# External imports
from fastapi import HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from app.logging_config import logger

# Self imports
from app.services.apikey_services import validate_api_key
from app.utils.url_utils import normalize_original_url, generate_short_url
from models import ShortenerCreate, ShortenerLink
from db import SessionDep

MAX_ATTEMPTS = 5
SHORT_URL_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")
METRICS_SERVICE_URL = os.getenv("METRICS_SERVICE_URL")
TIMEOUT = .5


def create_shortener_link(session: SessionDep, original_url: str, short_url: str) -> ShortenerLink:

    try:
        new_link = ShortenerLink(
            original_url=original_url,
            short_url=short_url,
        )

        session.add(new_link)
        session.commit()
        session.refresh(new_link)
        logger.info(f"Created new short URL: ({short_url}) -> {original_url}")
        return new_link
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating link: ({short_url}): {e}")
        raise

# Endpoint services


def create_link(payload: ShortenerCreate, session: SessionDep):

    validate_api_key(session, payload.api_key)

    normalized_url = normalize_original_url(str(payload.original_url))

    short_url = payload.short_url

    if short_url:
        if not SHORT_URL_PATTERN.match(short_url):
            logger.error(f"Invalid short URL format: {short_url}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Short URL not valid, only alphanumeric characters, hyphens, and underscores are allowed."
            )
        if len(short_url) < 3 or len(short_url) > 20:
            logger.error(f"Short URL length invalid: {short_url}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Short URL must be between 3 and 20 characters long."
            )

        try:
            return create_shortener_link(session, normalized_url, short_url)

        except IntegrityError as e:
            session.rollback()

            error_msg = str(e).lower()
            if "unique" in error_msg or "duplicate" in error_msg or "violates unique constraint" in error_msg:
                logger.warning(f"Short URL already exists: {short_url}")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Short URL already exists. Please choose another one."
                ) from e
            else:
                logger.error(f"Database integrity error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database integrity error occurred."
                ) from e

    else:
        for _ in range(MAX_ATTEMPTS):
            generated_short_url = generate_short_url()

            try:
                return create_shortener_link(session, normalized_url, generated_short_url)

            except IntegrityError as e:
                session.rollback()
                error_msg = str(e).lower()
                if not any(x in error_msg for x in ["unique", "duplicate", "violates unique constraint"]):
                    logger.error(f"Database integrity error: {e}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Database integrity error occurred."
                    ) from e
                continue

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Could not generate a unique short URL. Please try again."
    )


def deactivate_short_url(short_url: str, api_key: str, session: SessionDep):

    validate_api_key(session, api_key)

    link = session.exec(select(ShortenerLink).where(
        ShortenerLink.short_url == short_url)).first()

    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found."
        )

    if not link.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Short URL is already deactivated."
        )

    link.deleted_at = datetime.now(timezone.utc)
    link.is_active = False
    session.add(link)
    session.commit()
    session.refresh(link)
    logger.info(f"Short URL deactivated: {short_url}")
    return {"detail": "Short URL deactivated successfully."}


def get_links(session: SessionDep):

    links = session.exec(select(ShortenerLink).where(
        ShortenerLink.is_active == True)).all()
    return links


async def get_link(short_url: str, request: Request, session: SessionDep):

    link = session.exec(select(ShortenerLink).where(
        ShortenerLink.short_url == short_url, ShortenerLink.is_active == True)).first()

    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found or has been deleted."
        )

    headers_dict = dict(request.headers)
    data = {
        "link_id": str(link.id),
        "short_url": short_url,
        "ip": request.client.host if request.client else None,
        "user_agent": headers_dict.get("user-agent"),
        "referer": headers_dict.get("referer"),
        "accept_language": headers_dict.get("accept-language"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if METRICS_SERVICE_URL:
        try:
            async with httpx.AsyncClient() as client:
                await client.post(METRICS_SERVICE_URL, json=data, timeout=TIMEOUT)
                logger.info(f"Metrics data sent successfully: {data}")
        except httpx.RequestError as e:
            logger.warning(
                f"Metrics service unreachable: {type(e).__name__}: {e}")
            pass

    return RedirectResponse(link.original_url)
