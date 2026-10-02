from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import app.models  # noqa: F401 - register all models
from app.db.database import Base
from app.models.conversation_session import ConversationSession
from app.models.utterance import SpeakerType, Utterance
from app.providers.dummy_embedding_provider import DummyEmbeddingProvider
from app.providers.dummy_knowledge_model import DummyKnowledgeModel
from app.providers.knowledge_extraction_schema import KnowledgeExtraction
from app.repositories.keyword_repository import KeywordRepository
from app.repositories.knowledge_relation_repository import KnowledgeRelationRepository
from app.repositories.knowledge_repository import KnowledgeRepository
from app.services.knowledge_extraction_service import KnowledgeExtractionService
from app.services.knowledge_relation_service import KnowledgeRelationService


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


def _make_utterance(db: Session, session_id: int) -> Utterance:
    utterance = Utterance(
        session_id=session_id,
        speaker=SpeakerType.user,
        text="test",
        timestamp=datetime.now(timezone.utc),
        sequence_number=1,
    )
    db.add(utterance)
    db.flush()
    return utterance


def test_extract_returns_knowledge_with_correct_session_id() -> None:
    """extract() should return a persisted Knowledge with an id and the given session_id."""
    with Session(_make_engine()) as db:
        cs = ConversationSession(started_at=datetime.now(timezone.utc))
        db.add(cs)
        db.flush()
        utterance = _make_utterance(db, cs.id)

        service = _make_service(db)
        ks = service.extract(session_id=cs.id, utterances=[utterance])

        assert len(ks) == 1
        assert ks[0].id is not None
        assert ks[0].session_id == cs.id


def test_extract_sets_fields_from_model() -> None:
    """extract() should populate Knowledge fields with values returned by the model."""
    with Session(_make_engine()) as db:
        cs = ConversationSession(started_at=datetime.now(timezone.utc))
        db.add(cs)
        db.flush()
        utterance = _make_utterance(db, cs.id)

        service = _make_service(db)
        ks = service.extract(session_id=cs.id, utterances=[utterance])

        assert ks[0].title == "dummy title"
        assert ks[0].question == "dummy question"
        assert ks[0].summary == "dummy summary"
        assert ks[0].category == "dummy category"
        assert ks[0].related_questions == ["dummy related question"]


def test_extract_associates_keyword_with_knowledge() -> None:
    """extract() should associate keywords returned by the model with the Knowledge."""
    with Session(_make_engine()) as db:
        cs = ConversationSession(started_at=datetime.now(timezone.utc))
        db.add(cs)
        db.flush()
        utterance = _make_utterance(db, cs.id)

        service = _make_service(db)
        ks = service.extract(session_id=cs.id, utterances=[utterance])

        keyword_repo = KeywordRepository(db)
        keywords = keyword_repo.list_for_knowledge(ks[0].id)

        assert len(keywords) == 1
        assert keywords[0].name == "dummy keyword"


def test_extract_sets_question_to_none_when_no_questions() -> None:
    """extract() should set question to None when the model returns question=None."""

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

        def extract_knowledge(self, utterances: list[Utterance]) -> list[KnowledgeExtraction]:
            return [KnowledgeExtraction(
                title="t",
                question=None,
                summary="s",
                answer="",
                category="c",
                keywords=[],
            )]

    with Session(_make_engine()) as db:
        cs = ConversationSession(started_at=datetime.now(timezone.utc))
        db.add(cs)
        db.flush()
        utterance = _make_utterance(db, cs.id)

        service = KnowledgeExtractionService(
            db=db,
            knowledge_repo=KnowledgeRepository(db),
            keyword_repo=KeywordRepository(db),
            model=NoQuestionsModel(),
        )
        ks = service.extract(session_id=cs.id, utterances=[utterance])

        assert ks[0].question is None


def test_extract_creates_multiple_knowledge_items() -> None:
    """extract() should create one Knowledge record per item returned by the model."""

    class MultiTopicModel:
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

        def extract_knowledge(self, utterances: list[Utterance]) -> list[KnowledgeExtraction]:
            return [
                KnowledgeExtraction(
                    title="title1",
                    question="question1",
                    summary="summary1",
                    answer="answer1",
                    category="category1",
                    keywords=["kw1"],
                ),
                KnowledgeExtraction(
                    title="title2",
                    question="question2",
                    summary="summary2",
                    answer="answer2",
                    category="category2",
                    keywords=["kw2"],
                ),
            ]

    with Session(_make_engine()) as db:
        cs = ConversationSession(started_at=datetime.now(timezone.utc))
        db.add(cs)
        db.flush()
        utterance = _make_utterance(db, cs.id)

        service = KnowledgeExtractionService(
            db=db,
            knowledge_repo=KnowledgeRepository(db),
            keyword_repo=KeywordRepository(db),
            model=MultiTopicModel(),
        )
        ks = service.extract(session_id=cs.id, utterances=[utterance])

        assert len(ks) == 2
        assert ks[0].title == "title1"
        assert ks[1].title == "title2"
        assert ks[0].session_id == cs.id
        assert ks[1].session_id == cs.id


def test_extract_returns_empty_list_when_no_utterances() -> None:
    """extract() should return [] without calling the model when utterances is empty."""
    with Session(_make_engine()) as db:
        cs = ConversationSession(started_at=datetime.now(timezone.utc))
        db.add(cs)
        db.flush()

        service = _make_service(db)
        result = service.extract(session_id=cs.id, utterances=[])

        assert result == []


def test_extract_returns_existing_knowledge_without_calling_model_again() -> None:
    """extract() called twice should return existing Knowledge on the second call."""
    with Session(_make_engine()) as db:
        cs = ConversationSession(started_at=datetime.now(timezone.utc))
        db.add(cs)
        db.flush()
        utterance = _make_utterance(db, cs.id)

        service = _make_service(db)
        first = service.extract(session_id=cs.id, utterances=[utterance])
        second = service.extract(session_id=cs.id, utterances=[utterance])

        assert len(second) == len(first)
        assert [k.id for k in second] == [k.id for k in first]


def test_extract_stores_embedding_when_provider_given() -> None:
    """extract() should store an embedding when EmbeddingProvider is configured."""
    with Session(_make_engine()) as db:
        cs = ConversationSession(started_at=datetime.now(timezone.utc))
        db.add(cs)
        db.flush()
        utterance = _make_utterance(db, cs.id)

        service = KnowledgeExtractionService(
            db=db,
            knowledge_repo=KnowledgeRepository(db),
            keyword_repo=KeywordRepository(db),
            model=DummyKnowledgeModel(),
            embedding_provider=DummyEmbeddingProvider(),
        )
        ks = service.extract(session_id=cs.id, utterances=[utterance])

        db.refresh(ks[0])
        assert ks[0].embedding is not None


def test_extract_does_not_store_embedding_when_no_provider() -> None:
    """extract() should leave embedding as None when no EmbeddingProvider is given."""
    with Session(_make_engine()) as db:
        cs = ConversationSession(started_at=datetime.now(timezone.utc))
        db.add(cs)
        db.flush()
        utterance = _make_utterance(db, cs.id)

        service = _make_service(db)  # no embedding_provider
        ks = service.extract(session_id=cs.id, utterances=[utterance])

        assert ks[0].embedding is None


def test_extract_continues_when_embedding_fails() -> None:
    """extract() should persist Knowledge even if embed_text() raises an exception."""

    class FailingEmbeddingProvider:
        def embed_text(self, text: str) -> list[float]:
            raise RuntimeError("embedding API error")

    with Session(_make_engine()) as db:
        cs = ConversationSession(started_at=datetime.now(timezone.utc))
        db.add(cs)
        db.flush()
        utterance = _make_utterance(db, cs.id)

        service = KnowledgeExtractionService(
            db=db,
            knowledge_repo=KnowledgeRepository(db),
            keyword_repo=KeywordRepository(db),
            model=DummyKnowledgeModel(),
            embedding_provider=FailingEmbeddingProvider(),
        )
        ks = service.extract(session_id=cs.id, utterances=[utterance])

        # Knowledge should be persisted despite embedding failure
        assert len(ks) == 1
        assert ks[0].id is not None


def test_extract_calls_relation_service_when_provided() -> None:
    """extract() should call generate_relations_for_knowledge() when relation_service is given."""
    calls: list[int] = []

    class SpyRelationService:
        def generate_relations_for_knowledge(self, knowledge_id: int) -> list:
            calls.append(knowledge_id)
            return []

    with Session(_make_engine()) as db:
        cs = ConversationSession(started_at=datetime.now(timezone.utc))
        db.add(cs)
        db.flush()
        utterance = _make_utterance(db, cs.id)

        knowledge_repo = KnowledgeRepository(db)
        service = KnowledgeExtractionService(
            db=db,
            knowledge_repo=knowledge_repo,
            keyword_repo=KeywordRepository(db),
            model=DummyKnowledgeModel(),
            relation_service=SpyRelationService(),
        )
        ks = service.extract(session_id=cs.id, utterances=[utterance])

        assert len(ks) == 1
        assert ks[0].id in calls


def test_extract_continues_when_relation_service_fails() -> None:
    """extract() should persist Knowledge even if generate_relations_for_knowledge() raises."""

    class FailingRelationService:
        def generate_relations_for_knowledge(self, knowledge_id: int) -> list:
            raise RuntimeError("relation generation error")

    with Session(_make_engine()) as db:
        cs = ConversationSession(started_at=datetime.now(timezone.utc))
        db.add(cs)
        db.flush()
        utterance = _make_utterance(db, cs.id)

        knowledge_repo = KnowledgeRepository(db)
        service = KnowledgeExtractionService(
            db=db,
            knowledge_repo=knowledge_repo,
            keyword_repo=KeywordRepository(db),
            model=DummyKnowledgeModel(),
            relation_service=FailingRelationService(),
        )
        ks = service.extract(session_id=cs.id, utterances=[utterance])

        assert len(ks) == 1
        assert ks[0].id is not None
