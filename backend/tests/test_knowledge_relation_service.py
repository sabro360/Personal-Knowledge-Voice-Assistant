from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import app.models  # noqa: F401 - register all models
from app.db.database import Base
from app.repositories.knowledge_relation_repository import KnowledgeRelationRepository
from app.repositories.knowledge_repository import KnowledgeRepository
from app.services.knowledge_relation_service import KnowledgeRelationService


def _make_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return Session(engine)


def _make_service(db: Session) -> KnowledgeRelationService:
    return KnowledgeRelationService(
        knowledge_repo=KnowledgeRepository(db),
        relation_repo=KnowledgeRelationRepository(db),
    )


def test_generate_relations_returns_empty_list_on_sqlite() -> None:
    """generate_relations_for_knowledge() should return [] on SQLite (no pgvector)."""
    with _make_db() as db:
        service = _make_service(db)
        result = service.generate_relations_for_knowledge(knowledge_id=1)

        assert result == []


def test_generate_relations_returns_empty_list_for_missing_knowledge() -> None:
    """generate_relations_for_knowledge() should return [] when knowledge_id does not exist."""
    with _make_db() as db:
        service = _make_service(db)
        # No Knowledge with id=999 in DB; find_similar returns [] (SQLite no-op too)
        result = service.generate_relations_for_knowledge(knowledge_id=999)

        assert result == []
