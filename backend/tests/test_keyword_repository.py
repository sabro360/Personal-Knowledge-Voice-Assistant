from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import app.models  # noqa: F401 - register all models (needed for FK tables)
from app.db.database import Base
from app.models.knowledge_keyword import KnowledgeKeyword
from app.repositories.keyword_repository import KeywordRepository


def _make_engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


def test_get_or_create_creates_new_keyword() -> None:
    """get_or_create() should create a new Keyword when the name does not exist."""
    with Session(_make_engine()) as db:
        repo = KeywordRepository(db)
        k = repo.get_or_create("光学")

        assert k.id is not None
        assert k.name == "光学"


def test_get_or_create_returns_existing_keyword() -> None:
    """get_or_create() should return the existing Keyword without creating a duplicate."""
    with Session(_make_engine()) as db:
        repo = KeywordRepository(db)
        k1 = repo.get_or_create("光学")
        k2 = repo.get_or_create("光学")

        assert k1.id == k2.id


def test_list_for_knowledge_returns_associated_keywords() -> None:
    """list_for_knowledge() should return all Keywords linked to the given knowledge_id."""
    with Session(_make_engine()) as db:
        repo = KeywordRepository(db)
        k1 = repo.get_or_create("光学")
        k2 = repo.get_or_create("回折")
        db.add(KnowledgeKeyword(knowledge_id=1, keyword_id=k1.id))
        db.add(KnowledgeKeyword(knowledge_id=1, keyword_id=k2.id))
        db.commit()

        keywords = repo.list_for_knowledge(1)

        assert len(keywords) == 2
        names = {kw.name for kw in keywords}
        assert names == {"光学", "回折"}


def test_list_for_knowledge_returns_empty_list_when_no_keywords() -> None:
    """list_for_knowledge() should return an empty list when no keywords are associated."""
    with Session(_make_engine()) as db:
        repo = KeywordRepository(db)

        assert repo.list_for_knowledge(9999) == []


def test_list_for_knowledge_returns_only_target_knowledge_keywords() -> None:
    """list_for_knowledge() should not return keywords linked to other knowledge items."""
    with Session(_make_engine()) as db:
        repo = KeywordRepository(db)
        k1 = repo.get_or_create("光学")
        k2 = repo.get_or_create("音波")
        db.add(KnowledgeKeyword(knowledge_id=1, keyword_id=k1.id))
        db.add(KnowledgeKeyword(knowledge_id=2, keyword_id=k2.id))
        db.commit()

        keywords = repo.list_for_knowledge(1)

        assert len(keywords) == 1
        assert keywords[0].name == "光学"
