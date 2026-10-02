from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import app.models  # noqa: F401 - register all models (needed for FK to conversation_sessions)
from app.db.database import Base
from app.models.conversation_session import ConversationSession
from app.repositories.knowledge_repository import KnowledgeRepository


def _make_engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


def test_create_returns_knowledge_with_id() -> None:
    """create() should persist a Knowledge item and return it with an id and timestamps."""
    with Session(_make_engine()) as db:
        cs = ConversationSession(started_at=datetime.now(timezone.utc))
        db.add(cs)
        db.flush()

        repo = KnowledgeRepository(db)
        k = repo.create(session_id=cs.id)

        assert k.id is not None
        assert k.session_id == cs.id
        assert k.created_at is not None
        assert k.updated_at is not None


def test_create_stores_optional_fields() -> None:
    """create() should persist all optional fields when provided."""
    with Session(_make_engine()) as db:
        cs = ConversationSession(started_at=datetime.now(timezone.utc))
        db.add(cs)
        db.flush()

        repo = KnowledgeRepository(db)
        k = repo.create(
            session_id=cs.id,
            title="CDが虹色な理由",
            question="なぜCDは虹色に見えるの？",
            summary="光の回折による干渉",
            answer="CDの溝が回折格子として機能する",
            category="物理",
        )

        assert k.title == "CDが虹色な理由"
        assert k.question == "なぜCDは虹色に見えるの？"
        assert k.summary == "光の回折による干渉"
        assert k.answer == "CDの溝が回折格子として機能する"
        assert k.category == "物理"


def test_get_by_id_returns_existing_knowledge() -> None:
    """get_by_id() should return the Knowledge item for a known ID."""
    with Session(_make_engine()) as db:
        cs = ConversationSession(started_at=datetime.now(timezone.utc))
        db.add(cs)
        db.flush()

        repo = KnowledgeRepository(db)
        k = repo.create(session_id=cs.id, title="CDが虹色な理由")

        found = repo.get_by_id(k.id)

        assert found is not None
        assert found.id == k.id
        assert found.title == "CDが虹色な理由"


def test_get_by_id_returns_none_for_missing_id() -> None:
    """get_by_id() should return None when the ID does not exist."""
    with Session(_make_engine()) as db:
        repo = KnowledgeRepository(db)

        assert repo.get_by_id(9999) is None


def test_list_returns_all_knowledge_items() -> None:
    """list() should return all Knowledge items."""
    with Session(_make_engine()) as db:
        cs = ConversationSession(started_at=datetime.now(timezone.utc))
        db.add(cs)
        db.flush()

        repo = KnowledgeRepository(db)
        repo.create(session_id=cs.id, title="知識1")
        repo.create(session_id=cs.id, title="知識2")

        items = repo.list()

        assert len(items) == 2
        titles = {item.title for item in items}
        assert titles == {"知識1", "知識2"}


def test_list_returns_empty_list_when_no_knowledge() -> None:
    """list() should return an empty list when no Knowledge items exist."""
    with Session(_make_engine()) as db:
        repo = KnowledgeRepository(db)

        assert repo.list() == []


def test_update_replaces_fields() -> None:
    """update() should replace all updatable fields and return the updated item."""
    with Session(_make_engine()) as db:
        cs = ConversationSession(started_at=datetime.now(timezone.utc))
        db.add(cs)
        db.flush()

        repo = KnowledgeRepository(db)
        k = repo.create(session_id=cs.id, title="旧タイトル", category="旧カテゴリ")

        updated = repo.update(
            knowledge_id=k.id,
            title="新タイトル",
            question="新質問",
            summary="新要約",
            answer="新回答",
            category="新カテゴリ",
        )

        assert updated is not None
        assert updated.id == k.id
        assert updated.title == "新タイトル"
        assert updated.question == "新質問"
        assert updated.summary == "新要約"
        assert updated.answer == "新回答"
        assert updated.category == "新カテゴリ"


def test_update_returns_none_for_missing_id() -> None:
    """update() should return None when the knowledge_id does not exist."""
    with Session(_make_engine()) as db:
        repo = KnowledgeRepository(db)

        result = repo.update(
            knowledge_id=9999,
            title="タイトル",
            question=None,
            summary=None,
            answer=None,
            category=None,
        )

        assert result is None


def test_search_returns_matching_knowledge_by_title() -> None:
    """search() should return Knowledge items matching the query in title."""
    with Session(_make_engine()) as db:
        cs = ConversationSession(started_at=datetime.now(timezone.utc))
        db.add(cs)
        db.flush()

        repo = KnowledgeRepository(db)
        repo.create(session_id=cs.id, title="CDの虹色の仕組み", summary="光の回折")
        repo.create(session_id=cs.id, title="水滴と光の関係", summary="虹の仕組み")

        results = repo.search("CD")

        assert len(results) == 1
        assert results[0].title == "CDの虹色の仕組み"


def test_search_returns_matching_knowledge_by_question() -> None:
    """search() should return Knowledge items matching the query in question."""
    with Session(_make_engine()) as db:
        cs = ConversationSession(started_at=datetime.now(timezone.utc))
        db.add(cs)
        db.flush()

        repo = KnowledgeRepository(db)
        repo.create(session_id=cs.id, question="なぜ空は青いのか", summary="光の散乱")

        results = repo.search("空は青い")

        assert len(results) == 1
        assert results[0].question == "なぜ空は青いのか"


def test_search_returns_empty_list_when_no_match() -> None:
    """search() should return an empty list when no Knowledge items match."""
    with Session(_make_engine()) as db:
        cs = ConversationSession(started_at=datetime.now(timezone.utc))
        db.add(cs)
        db.flush()

        repo = KnowledgeRepository(db)
        repo.create(session_id=cs.id, title="量子力学の基礎", summary="波動関数")

        results = repo.search("全く関係ないキーワード")

        assert results == []


def test_search_is_case_insensitive() -> None:
    """search() should match regardless of case."""
    with Session(_make_engine()) as db:
        cs = ConversationSession(started_at=datetime.now(timezone.utc))
        db.add(cs)
        db.flush()

        repo = KnowledgeRepository(db)
        repo.create(session_id=cs.id, title="Python programming basics", summary="vars")

        results_lower = repo.search("python")
        results_upper = repo.search("PYTHON")

        assert len(results_lower) == 1
        assert len(results_upper) == 1


def test_list_by_session_returns_knowledge_for_session() -> None:
    """list_by_session() should return Knowledge items for the given session."""
    with Session(_make_engine()) as db:
        cs = ConversationSession(started_at=datetime.now(timezone.utc))
        db.add(cs)
        db.flush()

        repo = KnowledgeRepository(db)
        repo.create(session_id=cs.id, title="知識1")
        repo.create(session_id=cs.id, title="知識2")

        items = repo.list_by_session(cs.id)

        assert len(items) == 2
        titles = {item.title for item in items}
        assert titles == {"知識1", "知識2"}


def test_list_by_session_returns_empty_list_when_no_knowledge() -> None:
    """list_by_session() should return [] when no Knowledge exists for the session."""
    with Session(_make_engine()) as db:
        cs = ConversationSession(started_at=datetime.now(timezone.utc))
        db.add(cs)
        db.flush()

        repo = KnowledgeRepository(db)

        assert repo.list_by_session(cs.id) == []


def test_list_by_session_returns_only_knowledge_for_given_session() -> None:
    """list_by_session() should not include Knowledge from other sessions."""
    with Session(_make_engine()) as db:
        cs1 = ConversationSession(started_at=datetime.now(timezone.utc))
        cs2 = ConversationSession(started_at=datetime.now(timezone.utc))
        db.add(cs1)
        db.add(cs2)
        db.flush()

        repo = KnowledgeRepository(db)
        repo.create(session_id=cs1.id, title="セッション1の知識")
        repo.create(session_id=cs2.id, title="セッション2の知識")

        items = repo.list_by_session(cs1.id)

        assert len(items) == 1
        assert items[0].title == "セッション1の知識"


def test_update_embedding_stores_vector() -> None:
    """update_embedding() should persist the embedding vector on a Knowledge item."""
    with Session(_make_engine()) as db:
        cs = ConversationSession(started_at=datetime.now(timezone.utc))
        db.add(cs)
        db.flush()

        repo = KnowledgeRepository(db)
        k = repo.create(session_id=cs.id, title="テスト知識")
        assert k.embedding is None

        vec = [0.01] * 1536
        repo.update_embedding(k.id, vec)
        db.refresh(k)

        assert k.embedding is not None


def test_update_embedding_does_nothing_for_missing_id() -> None:
    """update_embedding() should not raise an error when knowledge_id does not exist."""
    with Session(_make_engine()) as db:
        repo = KnowledgeRepository(db)
        repo.update_embedding(9999, [0.0] * 1536)  # should not raise


def test_semantic_search_returns_empty_list_on_sqlite() -> None:
    """semantic_search() should return [] on non-PostgreSQL databases."""
    with Session(_make_engine()) as db:
        cs = ConversationSession(started_at=datetime.now(timezone.utc))
        db.add(cs)
        db.flush()

        repo = KnowledgeRepository(db)
        repo.create(session_id=cs.id, title="テスト知識")

        # SQLite does not support vector similarity — must return empty list
        results = repo.semantic_search([0.01] * 1536)
        assert results == []
