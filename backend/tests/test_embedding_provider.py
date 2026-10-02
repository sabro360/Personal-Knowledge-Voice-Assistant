from app.providers.dummy_embedding_provider import DummyEmbeddingProvider


def test_dummy_embed_text_returns_correct_dimensions() -> None:
    """DummyEmbeddingProvider.embed_text() should return a list of 1536 floats."""
    provider = DummyEmbeddingProvider()
    result = provider.embed_text("test text")

    assert isinstance(result, list)
    assert len(result) == DummyEmbeddingProvider.DIMS
    assert len(result) == 1536


def test_dummy_embed_text_returns_floats() -> None:
    """DummyEmbeddingProvider.embed_text() should return a list of float values."""
    provider = DummyEmbeddingProvider()
    result = provider.embed_text("some text")

    assert all(isinstance(v, float) for v in result)


def test_dummy_embed_text_is_deterministic() -> None:
    """DummyEmbeddingProvider.embed_text() should return the same vector for any input."""
    provider = DummyEmbeddingProvider()
    result1 = provider.embed_text("text one")
    result2 = provider.embed_text("completely different text")

    assert result1 == result2
