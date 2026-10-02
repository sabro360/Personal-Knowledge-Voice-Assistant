import logging

from app.models.knowledge_relation import KnowledgeRelation
from app.repositories.knowledge_relation_repository import KnowledgeRelationRepository
from app.repositories.knowledge_repository import KnowledgeRepository

logger = logging.getLogger(__name__)

SIMILARITY_THRESHOLD = 0.25  # cosine distance ≤ 0.25 → cosine similarity ≥ 0.75
RELATION_TYPE = "similar"
MAX_RELATIONS_PER_KNOWLEDGE = 5


class KnowledgeRelationService:
    """Service for automatically generating similarity-based Knowledge relations."""

    def __init__(
        self,
        knowledge_repo: KnowledgeRepository,
        relation_repo: KnowledgeRelationRepository,
    ) -> None:
        """Initialize with repository dependencies."""
        self._knowledge_repo = knowledge_repo
        self._relation_repo = relation_repo

    def generate_relations_for_knowledge(self, knowledge_id: int) -> list[KnowledgeRelation]:
        """Find similar Knowledge items and persist relations.

        Uses pgvector cosine distance. No-op on SQLite (find_similar returns []).
        Normalizes source_id < target_id to prevent bidirectional duplicates.
        """
        similar = self._knowledge_repo.find_similar(
            knowledge_id,
            threshold=SIMILARITY_THRESHOLD,
            limit=MAX_RELATIONS_PER_KNOWLEDGE,
        )
        results: list[KnowledgeRelation] = []
        for other, score in similar:
            src = min(knowledge_id, other.id)
            tgt = max(knowledge_id, other.id)
            if not self._relation_repo.exists(src, tgt):
                rel = self._relation_repo.create(src, tgt, RELATION_TYPE, score)
                results.append(rel)
                logger.debug(
                    "Created relation %d <-> %d (score=%.3f)", src, tgt, score
                )
        return results
