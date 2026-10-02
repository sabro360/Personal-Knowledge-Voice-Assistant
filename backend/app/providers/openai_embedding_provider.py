from openai import OpenAI

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMS = 1536


class OpenAIEmbeddingProvider:
    """EmbeddingProvider using OpenAI text-embedding-3-small (1536 dimensions)."""

    def __init__(self, api_key: str) -> None:
        """Initialize with an OpenAI API key."""
        self._client = OpenAI(api_key=api_key)

    def embed_text(self, text: str) -> list[float]:
        """Call OpenAI Embeddings API and return a 1536-dim float vector."""
        response = self._client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text,
            dimensions=EMBEDDING_DIMS,
        )
        return response.data[0].embedding
