from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import app.models  # noqa: F401 - register all models
from app.db.database import Base
from app.models.knowledge_relation import KnowledgeRelation


def test_knowledge_relation_tablename() -> None:
    """KnowledgeRelation should map to knowledge_relations table."""
    assert KnowledgeRelation.__tablename__ == "knowledge_relations"


def test_knowledge_relation_columns() -> None:
    """KnowledgeRelation should have all required columns."""
    columns = {col.name for col in KnowledgeRelation.__table__.columns}
    assert columns == {
        "id",
        "source_knowledge_id",
        "target_knowledge_id",
        "relation_type",
        "score",
        "created_at",
    }


def test_knowledge_relation_insert_and_retrieve() -> None:
    """KnowledgeRelation should be insertable and retrievable via in-memory SQLite."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        rel = KnowledgeRelation(
            source_knowledge_id=1,
            target_knowledge_id=2,
            relation_type="similar",
            score=0.85,
        )
        session.add(rel)
        session.commit()
        session.refresh(rel)

        assert rel.id is not None
        assert rel.source_knowledge_id == 1
        assert rel.target_knowledge_id == 2
        assert rel.relation_type == "similar"
        assert rel.score == 0.85
        assert rel.created_at is not None
