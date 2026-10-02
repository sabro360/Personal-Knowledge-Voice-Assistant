class DummyEmbeddingProvider:
    """Fixed-vector EmbeddingProvider for testing purposes."""

    DIMS = 1536

    def embed_text(self, text: str) -> list[float]:
        """Return a fixed 1536-dim vector regardless of input."""
        return [0.01] * self.DIMS
