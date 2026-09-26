from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import app.models  # noqa: F401 - register all models (needed for FK to conversation_sessions)
from app.db.database import Base
from app.models.knowledge import Knowledge


def test_knowledge_tablename() -> None:
    """Knowledge should map to knowledge table."""
    assert Knowledge.__tablename__ == "knowledge"


def test_knowledge_columns() -> None:
    """Knowledge should have all required columns."""
    columns = {col.name for col in Knowledge.__table__.columns}
    assert columns == {
        "id",
        "session_id",
        "title",
        "question",
        "summary",
        "answer",
        "category",
        "created_at",
        "updated_at",
    }


def test_knowledge_insert_and_retrieve() -> None:
    """Knowledge should be insertable and retrievable via in-memory SQLite."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        k = Knowledge(session_id=1, title="CDが虹色な理由")
        session.add(k)
        session.commit()
        session.refresh(k)

        assert k.id is not None
        assert k.session_id == 1
        assert k.title == "CDが虹色な理由"
        assert k.question is None
        assert k.summary is None
        assert k.answer is None
        assert k.category is None
        assert k.created_at is not None
        assert k.updated_at is not None
