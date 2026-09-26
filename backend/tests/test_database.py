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


def test_sqlite_connection_executes_query() -> None:
    """SQLite engine should be able to execute a simple query."""
    from sqlalchemy import text

    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1


def test_sqlite_allows_multithreaded_access() -> None:
    """SQLite engine should allow session access from multiple threads."""
    import threading

    from sqlalchemy import text

    errors: list[Exception] = []

    def use_session() -> None:
        try:
            session: Session = SessionLocal()
            session.execute(text("SELECT 1"))
            session.close()
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=use_session) for _ in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"Thread errors: {errors}"
