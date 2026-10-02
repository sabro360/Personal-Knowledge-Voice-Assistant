import pytest

from app.api.realtime import get_voice_provider
from app.api.sessions import (
    get_knowledge_model,
    get_optional_embedding_provider,
    get_optional_knowledge_model,
)
from app.main import app
from app.providers.dummy_embedding_provider import DummyEmbeddingProvider
from app.providers.dummy_knowledge_model import DummyKnowledgeModel
from app.providers.dummy_voice_provider import DummyVoiceProvider


@pytest.fixture(autouse=True)
def override_knowledge_model():
    """Prevent real OpenAI API calls in all tests by using DummyKnowledgeModel, DummyVoiceProvider, and DummyEmbeddingProvider."""
    app.dependency_overrides[get_knowledge_model] = lambda: DummyKnowledgeModel()
    app.dependency_overrides[get_optional_knowledge_model] = lambda: DummyKnowledgeModel()
    app.dependency_overrides[get_optional_embedding_provider] = lambda: DummyEmbeddingProvider()
    app.dependency_overrides[get_voice_provider] = lambda: DummyVoiceProvider()
    yield
    app.dependency_overrides.pop(get_knowledge_model, None)
    app.dependency_overrides.pop(get_optional_knowledge_model, None)
    app.dependency_overrides.pop(get_optional_embedding_provider, None)
    app.dependency_overrides.pop(get_voice_provider, None)
