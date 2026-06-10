"""Database session helper for FastAPI background tasks."""

from contextlib import contextmanager
from typing import Generator

from app.db.database import SessionLocal
from sqlalchemy.orm import Session


@contextmanager
def background_db() -> Generator[Session, None, None]:
    """Create a fresh DB session for background work (request sessions must not be reused)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
