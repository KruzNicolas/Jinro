
# Standard library imports
import string
import random
import uuid
import re
from datetime import datetime, timezone

# External imports
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import RedirectResponse
from sqlmodel import select
from sqlalchemy.exc import IntegrityError

# Self imports
from models import ShortenerCreate, ShortenerRead, ShortenerLink
from db import SessionDep

MAX_ATTEMPTS = 5
router = APIRouter()

# Generate a random short URL


def generate_short_url(length: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def normalize_original_url(url: str) -> str:
    pattern = r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, url):
        raise HTTPException(
            status_code=400,
            detail="Original URL inválido. Debe ser un dominio como 'example.com'."
        )

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    return url


def create_shortener_link(session: SessionDep, original_url: str, short_url: str) -> ShortenerLink:

    try:
        normalized_url = normalize_original_url(original_url)
        new_link = ShortenerLink(
            original_url=normalized_url,
            short_url=short_url,
        )

        session.add(new_link)
        session.commit()
        session.refresh(new_link)
        return new_link
    except Exception as e:
        session.rollback()
        raise


# Create a new short URL


@router.post("/links", response_model=ShortenerRead, status_code=status.HTTP_201_CREATED, tags=["shortener"])
def create_short_url(payload: ShortenerCreate, session: SessionDep):

    short_url = payload.short_url

    if short_url:
        if not re.match(r'^[a-zA-Z0-9_-]+$', short_url):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Short URL not valid, only alphanumeric characters, hyphens, and underscores are allowed."
            )
        if len(short_url) < 3 or len(short_url) > 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Short URL must be between 3 and 20 characters long."
            )

        try:
            return create_shortener_link(session, payload.original_url, short_url)

        except IntegrityError as e:
            session.rollback()

            error_msg = str(e).lower()
            if "unique" in error_msg or "duplicate" in error_msg or "violates unique constraint" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Short URL already exists. Please choose another one."
                ) from e
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database integrity error occurred."
                ) from e

    else:
        for _ in range(MAX_ATTEMPTS):
            candidate = generate_short_url()

            try:
                return create_shortener_link(session, payload.original_url, candidate)

            except IntegrityError as e:
                session.rollback()
                error_msg = str(e).lower()
                if not ("unique" in error_msg or "duplicate" in error_msg or "violates unique constraint" in error_msg):
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Database integrity error occurred."
                    ) from e
                continue

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Could not generate a unique short URL. Please try again."
    )


# Deactivate a short URL

@router.delete("/links/{short_url}", status_code=status.HTTP_200_OK, tags=["shortener"])
def delete_short_url(short_url: str, session: SessionDep):

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

    return {"detail": "Short URL deactivated successfully."}

# All link from a specific user


@router.get("/links", response_model=list[ShortenerRead], tags=["shortener"])
def get_all_links(session: SessionDep):

    links = session.exec(select(ShortenerLink).where(
        ShortenerLink.is_active == True)).all()
    return links

# Redirect to the original URL


@router.get("/{short_url}", tags=["shortener"])
def get_short_url(short_url: str, session: SessionDep):

    link = session.exec(select(ShortenerLink).where(
        ShortenerLink.short_url == short_url, ShortenerLink.is_active == True)).first()

    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found or has been deleted."
        )

    return RedirectResponse(link.original_url)
