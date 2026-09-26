from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.database import Base
from app.models.conversation_session import ConversationSession


def test_conversation_session_tablename() -> None:
    """ConversationSession should map to conversation_sessions table."""
    assert ConversationSession.__tablename__ == "conversation_sessions"


def test_conversation_session_columns() -> None:
    """ConversationSession should have all required columns."""
    columns = {col.name for col in ConversationSession.__table__.columns}
    assert columns == {"id", "started_at", "ended_at", "title", "created_at"}


def test_conversation_session_insert_and_retrieve() -> None:
    """ConversationSession should be insertable and retrievable via in-memory SQLite."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        cs = ConversationSession(started_at=datetime.now(timezone.utc))
        session.add(cs)
        session.commit()
        session.refresh(cs)

        assert cs.id is not None
        assert cs.started_at is not None
        assert cs.ended_at is None
        assert cs.title is None
        assert cs.created_at is not None
