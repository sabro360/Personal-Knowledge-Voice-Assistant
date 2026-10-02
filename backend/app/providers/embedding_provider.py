from typing import Protocol


class EmbeddingProvider(Protocol):
    """Protocol for text embedding services."""

    def embed_text(self, text: str) -> list[float]:
        """Embed a text string and return a float vector."""
        ...
