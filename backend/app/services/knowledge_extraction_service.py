import logging

from sqlalchemy.orm import Session

from app.models.knowledge import Knowledge
from app.models.knowledge_keyword import KnowledgeKeyword
from app.models.utterance import Utterance
from app.providers.embedding_provider import EmbeddingProvider
from app.providers.knowledge_model import KnowledgeModel
from app.repositories.keyword_repository import KeywordRepository
from app.repositories.knowledge_repository import KnowledgeRepository

logger = logging.getLogger(__name__)


def _build_embedding_text(knowledge: Knowledge) -> str:
    """Concatenate knowledge fields into a single string for embedding."""
    parts = [knowledge.title, knowledge.question, knowledge.summary, knowledge.answer]
    return " ".join(p for p in parts if p)


class KnowledgeExtractionService:
    """Service for extracting and persisting knowledge from a conversation."""

    def __init__(
        self,
        db: Session,
        knowledge_repo: KnowledgeRepository,
        keyword_repo: KeywordRepository,
        model: KnowledgeModel,
        embedding_provider: EmbeddingProvider | None = None,
    ) -> None:
        """Initialize with database session, repositories, knowledge model, and optional embedding provider."""
        self._db = db
        self._knowledge_repo = knowledge_repo
        self._keyword_repo = keyword_repo
        self._model = model
        self._embedding_provider = embedding_provider

    def extract(self, session_id: int, utterances: list[Utterance]) -> list[Knowledge]:
        """Extract knowledge from utterances and persist one Knowledge per topic.

        Calls the KnowledgeModel once to generate all knowledge items, then persists
        one Knowledge record per item. Keywords are extracted and associated via
        KnowledgeKeyword. If an EmbeddingProvider is configured, generates and stores
        embeddings for each item (failures are non-blocking). Returns the list of
        persisted Knowledge records.
        """
        if not utterances:
            return []
        existing = self._knowledge_repo.list_by_session(session_id)
        if existing:
            return existing
        extractions = self._model.extract_knowledge(utterances)
        results: list[Knowledge] = []

        for extraction in extractions:
            knowledge = self._knowledge_repo.create(
                session_id=session_id,
                title=extraction.title,
                question=extraction.question,
                summary=extraction.summary,
                category=extraction.category,
                related_questions=extraction.related_questions if extraction.related_questions else None,
            )
            for name in extraction.keywords:
                kw = self._keyword_repo.get_or_create(name)
                self._db.add(KnowledgeKeyword(knowledge_id=knowledge.id, keyword_id=kw.id))

            if self._embedding_provider is not None:
                try:
                    text = _build_embedding_text(knowledge)
                    vec = self._embedding_provider.embed_text(text)
                    self._knowledge_repo.update_embedding(knowledge.id, vec)
                except Exception as exc:
                    logger.warning(
                        "Embedding generation failed for knowledge %d: %s", knowledge.id, exc
                    )

            results.append(knowledge)

        self._db.commit()
        return results
