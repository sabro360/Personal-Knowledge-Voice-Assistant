from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import app.models  # noqa: F401 - register all models
from app.db.database import Base
from app.models.conversation_session import ConversationSession
from app.models.utterance import Utterance
from app.providers.dummy_knowledge_model import DummyKnowledgeModel
from app.providers.knowledge_extraction_schema import KnowledgeExtraction
from app.repositories.keyword_repository import KeywordRepository
from app.repositories.knowledge_repository import KnowledgeRepository
from app.services.knowledge_extraction_service import KnowledgeExtractionService


def _make_engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


def _make_service(db: Session) -> KnowledgeExtractionService:
    return KnowledgeExtractionService(
        db=db,
        knowledge_repo=KnowledgeRepository(db),
        keyword_repo=KeywordRepository(db),
        model=DummyKnowledgeModel(),
    )


def test_extract_returns_knowledge_with_correct_session_id() -> None:
    """extract() should return a persisted Knowledge with an id and the given session_id."""
    with Session(_make_engine()) as db:
        cs = ConversationSession(started_at=datetime.now(timezone.utc))
        db.add(cs)
        db.flush()

        service = _make_service(db)
        k = service.extract(session_id=cs.id, utterances=[])

        assert k.id is not None
        assert k.session_id == cs.id


def test_extract_sets_fields_from_model() -> None:
    """extract() should populate Knowledge fields with values returned by the model."""
    with Session(_make_engine()) as db:
        cs = ConversationSession(started_at=datetime.now(timezone.utc))
        db.add(cs)
        db.flush()

        service = _make_service(db)
        k = service.extract(session_id=cs.id, utterances=[])

        assert k.title == "dummy title"
        assert k.question == "dummy question"
        assert k.summary == "dummy summary"
        assert k.category == "dummy category"


def test_extract_associates_keyword_with_knowledge() -> None:
    """extract() should associate keywords returned by the model with the Knowledge."""
    with Session(_make_engine()) as db:
        cs = ConversationSession(started_at=datetime.now(timezone.utc))
        db.add(cs)
        db.flush()

        service = _make_service(db)
        k = service.extract(session_id=cs.id, utterances=[])

        keyword_repo = KeywordRepository(db)
        keywords = keyword_repo.list_for_knowledge(k.id)

        assert len(keywords) == 1
        assert keywords[0].name == "dummy keyword"


def test_extract_sets_question_to_none_when_no_questions() -> None:
    """extract() should set question to None when the model returns an empty questions list."""

    class NoQuestionsModel:
        def summarize_conversation(self, utterances: list[Utterance]) -> str:
            return "s"

        def extract_questions(self, utterances: list[Utterance]) -> list[str]:
            return []

        def extract_keywords(self, utterances: list[Utterance]) -> list[str]:
            return []

        def classify_category(self, utterances: list[Utterance]) -> str:
            return "c"

        def generate_title(self, utterances: list[Utterance]) -> str:
            return "t"

        def extract_knowledge(self, utterances: list[Utterance]) -> KnowledgeExtraction:
            return KnowledgeExtraction(
                title="t",
                question=None,
                summary="s",
                answer="",
                category="c",
                keywords=[],
            )

    with Session(_make_engine()) as db:
        cs = ConversationSession(started_at=datetime.now(timezone.utc))
        db.add(cs)
        db.flush()

        service = KnowledgeExtractionService(
            db=db,
            knowledge_repo=KnowledgeRepository(db),
            keyword_repo=KeywordRepository(db),
            model=NoQuestionsModel(),
        )
        k = service.extract(session_id=cs.id, utterances=[])

        assert k.question is None
