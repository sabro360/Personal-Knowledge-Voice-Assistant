from sqlalchemy.orm import Session

from app.models.knowledge import Knowledge
from app.models.knowledge_keyword import KnowledgeKeyword
from app.models.utterance import Utterance
from app.providers.knowledge_model import KnowledgeModel
from app.repositories.keyword_repository import KeywordRepository
from app.repositories.knowledge_repository import KnowledgeRepository


class KnowledgeExtractionService:
    """Service for extracting and persisting knowledge from a conversation."""

    def __init__(
        self,
        db: Session,
        knowledge_repo: KnowledgeRepository,
        keyword_repo: KeywordRepository,
        model: KnowledgeModel,
    ) -> None:
        """Initialize with database session, repositories, and knowledge model."""
        self._db = db
        self._knowledge_repo = knowledge_repo
        self._keyword_repo = keyword_repo
        self._model = model

    def extract(self, session_id: int, utterances: list[Utterance]) -> Knowledge:
        """Extract knowledge from utterances and persist as Knowledge with associated keywords.

        Calls the KnowledgeModel once to generate all fields, then persists a Knowledge
        record. Keywords are extracted and associated via KnowledgeKeyword. Returns the
        persisted Knowledge.
        """
        extraction = self._model.extract_knowledge(utterances)

        knowledge = self._knowledge_repo.create(
            session_id=session_id,
            title=extraction.title,
            question=extraction.question,
            summary=extraction.summary,
            category=extraction.category,
        )

        for name in extraction.keywords:
            kw = self._keyword_repo.get_or_create(name)
            self._db.add(KnowledgeKeyword(knowledge_id=knowledge.id, keyword_id=kw.id))
        self._db.commit()

        return knowledge
