from sqlalchemy.orm import DeclarativeBase, Session

from app.core.config import get_settings
from app.db.database import Base, SessionLocal, engine


def test_engine_url_matches_settings() -> None:
    """Engine should be created with the URL from settings."""
    settings = get_settings()
    assert str(engine.url) == settings.database_url


def test_session_local_creates_session() -> None:
    """SessionLocal should create a usable Session."""
    session: Session = SessionLocal()
    assert session is not None
    session.close()


def test_base_is_declarative_base() -> None:
    """Base should be a DeclarativeBase subclass for ORM models."""
    assert issubclass(Base, DeclarativeBase)
