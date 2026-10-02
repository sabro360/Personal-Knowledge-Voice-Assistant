from app.models.knowledge import Knowledge
from app.providers.embedding_provider import EmbeddingProvider
from app.repositories.knowledge_repository import KnowledgeRepository


class KnowledgeSearchService:
    """Service for searching the knowledge base."""

    def __init__(
        self,
        knowledge_repo: KnowledgeRepository,
        embedding_provider: EmbeddingProvider | None = None,
    ) -> None:
        """Initialize with a knowledge repository and optional embedding provider."""
        self._knowledge_repo = knowledge_repo
        self._embedding_provider = embedding_provider

    def search(self, query: str) -> list[Knowledge]:
        """Search knowledge items by text query.

        Searches title, question, summary, and answer fields using
        case-insensitive partial match. Returns results ordered by
        created_at descending. Returns an empty list if nothing matches.
        """
        return self._knowledge_repo.search(query)

    def semantic_search(self, query: str, limit: int = 10) -> list[Knowledge]:
        """Search knowledge items by semantic similarity to the query.

        Embeds the query using the EmbeddingProvider and returns results ordered
        by cosine similarity. Returns an empty list if no EmbeddingProvider is
        configured or the database does not support vector search.
        """
        if self._embedding_provider is None:
            return []
        vec = self._embedding_provider.embed_text(query)
        return self._knowledge_repo.semantic_search(vec, limit=limit)
