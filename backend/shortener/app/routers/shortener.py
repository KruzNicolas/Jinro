

# External imports
from fastapi import APIRouter, status, Request

# Self imports
from app.main import limiter
from services.shortener_service import create_link, deactivate_short_url, get_links, get_link
from models import ShortenerCreate, ShortenerRead
from db import SessionDep

router = APIRouter()


# Create a new short URL


@router.post("/links", response_model=ShortenerRead, status_code=status.HTTP_201_CREATED, tags=["shortener"])
def create_short_url(payload: ShortenerCreate, session: SessionDep):

    return create_link(payload, session)


# Deactivate a short URL

@router.delete("/links/{short_url}", status_code=status.HTTP_200_OK, tags=["shortener"])
def delete_short_url(short_url: str, api_key: str, session: SessionDep):
    return deactivate_short_url(short_url, api_key, session)


# Redirect to the original URL


@router.get("/{short_url}", tags=["shortener"])
@limiter.limit("15/minute")
def get_short_url(short_url: str, request: Request, session: SessionDep):
    return get_link(short_url, request, session)

# Get all short URLs


@router.get("/links", response_model=list[ShortenerRead], tags=["shortener"])
def get_all_links(session: SessionDep):
    return get_links(session)
