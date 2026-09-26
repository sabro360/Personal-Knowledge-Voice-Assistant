from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.database import Base
from app.repositories.conversation_session_repository import ConversationSessionRepository


def _make_engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


def test_create_returns_persisted_session() -> None:
    """create() should persist a ConversationSession and return it with an id."""
    with Session(_make_engine()) as db:
        repo = ConversationSessionRepository(db)
        started = datetime.now(timezone.utc)
        cs = repo.create(started_at=started)

        assert cs.id is not None
        assert cs.started_at == started.replace(tzinfo=None)
        assert cs.ended_at is None
        assert cs.created_at is not None


def test_get_by_id_returns_existing_session() -> None:
    """get_by_id() should return the ConversationSession for a known ID."""
    with Session(_make_engine()) as db:
        repo = ConversationSessionRepository(db)
        cs = repo.create(started_at=datetime.now(timezone.utc))

        found = repo.get_by_id(cs.id)

        assert found is not None
        assert found.id == cs.id


def test_get_by_id_returns_none_for_missing_id() -> None:
    """get_by_id() should return None when the ID does not exist."""
    with Session(_make_engine()) as db:
        repo = ConversationSessionRepository(db)

        assert repo.get_by_id(9999) is None


def test_list_returns_all_sessions_in_descending_order() -> None:
    """list() should return all sessions ordered by started_at descending."""
    with Session(_make_engine()) as db:
        repo = ConversationSessionRepository(db)
        earlier = datetime(2026, 1, 1, tzinfo=timezone.utc)
        later = datetime(2026, 6, 1, tzinfo=timezone.utc)
        repo.create(started_at=earlier)
        repo.create(started_at=later)

        sessions = repo.list()

        assert len(sessions) == 2
        assert sessions[0].started_at >= sessions[1].started_at


def test_list_returns_empty_list_when_no_sessions() -> None:
    """list() should return an empty list when no sessions exist."""
    with Session(_make_engine()) as db:
        repo = ConversationSessionRepository(db)

        assert repo.list() == []


def test_finish_sets_ended_at() -> None:
    """finish() should set ended_at on the target session and return it."""
    with Session(_make_engine()) as db:
        repo = ConversationSessionRepository(db)
        cs = repo.create(started_at=datetime.now(timezone.utc))
        ended = datetime(2026, 9, 26, 12, 0, 0, tzinfo=timezone.utc)

        result = repo.finish(session_id=cs.id, ended_at=ended)

        assert result is not None
        assert result.id == cs.id
        assert result.ended_at == ended.replace(tzinfo=None)


def test_finish_returns_none_for_missing_id() -> None:
    """finish() should return None when the session ID does not exist."""
    with Session(_make_engine()) as db:
        repo = ConversationSessionRepository(db)

        result = repo.finish(session_id=9999, ended_at=datetime.now(timezone.utc))

        assert result is None
