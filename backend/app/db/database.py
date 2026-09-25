from collections.abc import Generator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


def _create_engine() -> Engine:
    """Create database engine from application settings."""
    settings = get_settings()
    return create_engine(settings.database_url)


engine: Engine = _create_engine()

SessionLocal: sessionmaker[Session] = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    """Base class for all ORM models."""


def get_db() -> Generator[Session, None, None]:
    """Yield a database session for use as a FastAPI dependency."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
