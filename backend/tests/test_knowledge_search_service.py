from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import app.models  # noqa: F401 - register all models
from app.db.database import Base
from app.models.conversation_session import ConversationSession
from app.repositories.knowledge_repository import KnowledgeRepository
from app.services.knowledge_search_service import KnowledgeSearchService


def _make_engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


def _make_service(db: Session) -> KnowledgeSearchService:
    return KnowledgeSearchService(knowledge_repo=KnowledgeRepository(db))


def test_search_returns_matching_knowledge() -> None:
    """search() should return Knowledge items whose title matches the query."""
    with Session(_make_engine()) as db:
        cs = ConversationSession(started_at=datetime.now(timezone.utc))
        db.add(cs)
        db.flush()

        repo = KnowledgeRepository(db)
        repo.create(session_id=cs.id, title="CDの虹色の仕組み", summary="光の回折")
        repo.create(session_id=cs.id, title="飛行機が飛ぶ原理", summary="揚力")

        service = _make_service(db)
        results = service.search("CD")

        assert len(results) == 1
        assert results[0].title == "CDの虹色の仕組み"


def test_search_returns_empty_list_when_no_match() -> None:
    """search() should return an empty list when no Knowledge items match the query."""
    with Session(_make_engine()) as db:
        cs = ConversationSession(started_at=datetime.now(timezone.utc))
        db.add(cs)
        db.flush()

        repo = KnowledgeRepository(db)
        repo.create(session_id=cs.id, title="量子力学の基礎", summary="波動関数")

        service = _make_service(db)
        results = service.search("全く関係ないキーワード")

        assert results == []


def test_search_is_case_insensitive() -> None:
    """search() should match regardless of case."""
    with Session(_make_engine()) as db:
        cs = ConversationSession(started_at=datetime.now(timezone.utc))
        db.add(cs)
        db.flush()

        repo = KnowledgeRepository(db)
        repo.create(session_id=cs.id, title="Python programming basics", summary="variables")

        service = _make_service(db)
        results_lower = service.search("python")
        results_upper = service.search("PYTHON")

        assert len(results_lower) == 1
        assert len(results_upper) == 1


def test_semantic_search_returns_empty_list_when_no_provider() -> None:
    """semantic_search() should return [] when no EmbeddingProvider is configured."""
    with Session(_make_engine()) as db:
        service = KnowledgeSearchService(knowledge_repo=KnowledgeRepository(db))
        results = service.semantic_search("some query")
        assert results == []


def test_semantic_search_returns_empty_list_on_sqlite() -> None:
    """semantic_search() should return [] on SQLite (no pgvector support)."""
    from app.providers.dummy_embedding_provider import DummyEmbeddingProvider

    with Session(_make_engine()) as db:
        cs = ConversationSession(started_at=datetime.now(timezone.utc))
        db.add(cs)
        db.flush()

        repo = KnowledgeRepository(db)
        repo.create(session_id=cs.id, title="テスト知識")

        service = KnowledgeSearchService(
            knowledge_repo=repo,
            embedding_provider=DummyEmbeddingProvider(),
        )
        # SQLite does not support vector <=> operator — must return empty list
        results = service.semantic_search("test query")
        assert results == []
