from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import app.models  # noqa: F401 - register all models
from app.db.database import Base
from app.repositories.knowledge_relation_repository import KnowledgeRelationRepository


def _make_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return Session(engine)


def test_create_persists_relation() -> None:
    """create() should persist a KnowledgeRelation and return it with an id."""
    with _make_db() as db:
        repo = KnowledgeRelationRepository(db)
        rel = repo.create(source_id=1, target_id=2, relation_type="similar", score=0.9)

        assert rel.id is not None
        assert rel.source_knowledge_id == 1
        assert rel.target_knowledge_id == 2
        assert rel.relation_type == "similar"
        assert rel.score == 0.9
        assert rel.created_at is not None


def test_exists_returns_true_for_existing_relation() -> None:
    """exists() should return True when the relation has been created."""
    with _make_db() as db:
        repo = KnowledgeRelationRepository(db)
        repo.create(source_id=1, target_id=3, relation_type="similar", score=0.8)

        assert repo.exists(1, 3) is True


def test_exists_returns_false_for_missing_relation() -> None:
    """exists() should return False when no relation exists for the given pair."""
    with _make_db() as db:
        repo = KnowledgeRelationRepository(db)

        assert repo.exists(10, 20) is False


def test_list_all_returns_all_relations() -> None:
    """list_all() should return all persisted KnowledgeRelations."""
    with _make_db() as db:
        repo = KnowledgeRelationRepository(db)
        repo.create(source_id=1, target_id=2, relation_type="similar", score=0.9)
        repo.create(source_id=1, target_id=3, relation_type="similar", score=0.8)

        relations = repo.list_all()

        assert len(relations) == 2


def test_list_all_returns_empty_list_when_no_relations() -> None:
    """list_all() should return an empty list when there are no relations."""
    with _make_db() as db:
        repo = KnowledgeRelationRepository(db)

        assert repo.list_all() == []
