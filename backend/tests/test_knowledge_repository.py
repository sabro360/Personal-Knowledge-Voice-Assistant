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
