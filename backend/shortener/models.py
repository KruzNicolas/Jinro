
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
    user_id: uuid.UUID = Field(nullable=False, index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False)

# SCHEMAS (Pydantic)


class ShortenerCreate(BaseModel):
    original_url: str
    short_url: str | None = None
    user_id: uuid.UUID


class ShortenerRead(BaseModel):
    id: uuid.UUID
    original_url: str
    short_url: str
    user_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
