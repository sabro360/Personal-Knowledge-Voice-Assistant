from app.models.knowledge import Knowledge
from app.repositories.knowledge_repository import KnowledgeRepository


class KnowledgeSearchService:
    """Service for searching the knowledge base."""

    def __init__(self, knowledge_repo: KnowledgeRepository) -> None:
        """Initialize with a knowledge repository."""
        self._knowledge_repo = knowledge_repo

    def search(self, query: str) -> list[Knowledge]:
        """Search knowledge items by text query.

        Searches title, question, summary, and answer fields using
        case-insensitive partial match. Returns results ordered by
        created_at descending. Returns an empty list if nothing matches.
        """
        return self._knowledge_repo.search(query)
