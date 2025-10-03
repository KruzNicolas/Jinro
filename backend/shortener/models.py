
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field
from pydantic import BaseModel
import uuid

# DB


class ShortenerLink(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4,
                          primary_key=True)
    original_url: str = Field(nullable=False)
    short_url: str = Field(nullable=False, unique=True, index=True)
    is_active: bool = Field(default=True, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    deleted_at: datetime | None = Field(default=None, nullable=True)
    clicks: int = Field(default=0, nullable=False)

# SCHEMAS (Pydantic)


class ShortenerCreate(BaseModel):
    original_url: str
    short_url: str | None = None


class ShortenerRead(BaseModel):
    id: uuid.UUID
    original_url: str
    short_url: str
    is_active: bool
    created_at: datetime
    deleted_at: datetime | None = None

    class Config:
        from_attributes = True
