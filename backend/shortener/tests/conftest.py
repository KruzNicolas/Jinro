import hashlib
from models import ApiKey
from db import get_session
from app.main import app

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
import sys
import os

# Add the parent directory to sys.path to allow imports from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(name="session")
def session_fixture():
    # Use in-memory SQLite for testing
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="test_api_key")
def test_api_key_fixture(session: Session):
    raw_key = "test-secret-key"
    hashed_key = hashlib.sha256(raw_key.encode()).hexdigest()
    api_key = ApiKey(key_hash=hashed_key)
    session.add(api_key)
    session.commit()
    return raw_key
