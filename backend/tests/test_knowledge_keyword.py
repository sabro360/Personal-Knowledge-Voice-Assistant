import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import app.models  # noqa: F401 - register all models (needed for FK tables)
from app.db.database import Base
from app.models.knowledge_keyword import KnowledgeKeyword


def test_knowledge_keyword_tablename() -> None:
    """KnowledgeKeyword should map to knowledge_keywords table."""
    assert KnowledgeKeyword.__tablename__ == "knowledge_keywords"


def test_knowledge_keyword_columns() -> None:
    """KnowledgeKeyword should have knowledge_id and keyword_id columns."""
    columns = {col.name for col in KnowledgeKeyword.__table__.columns}
    assert columns == {"knowledge_id", "keyword_id"}


def test_knowledge_keyword_insert_and_retrieve() -> None:
    """KnowledgeKeyword should be insertable and retrievable via in-memory SQLite."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        kk = KnowledgeKeyword(knowledge_id=1, keyword_id=1)
        session.add(kk)
        session.commit()
        session.refresh(kk)

        assert kk.knowledge_id == 1
        assert kk.keyword_id == 1


def test_knowledge_keyword_composite_pk_prevents_duplicate() -> None:
    """Inserting the same (knowledge_id, keyword_id) pair should raise IntegrityError."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        session.add(KnowledgeKeyword(knowledge_id=1, keyword_id=1))
        session.commit()

    with Session(engine) as session:
        session.add(KnowledgeKeyword(knowledge_id=1, keyword_id=1))
        with pytest.raises(IntegrityError):
            session.commit()
