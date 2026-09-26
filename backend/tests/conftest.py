import pytest

from app.api.sessions import get_knowledge_model
from app.main import app
from app.providers.dummy_knowledge_model import DummyKnowledgeModel


@pytest.fixture(autouse=True)
def override_knowledge_model():
    """Prevent real OpenAI API calls in all tests by using DummyKnowledgeModel."""
    app.dependency_overrides[get_knowledge_model] = lambda: DummyKnowledgeModel()
    yield
    app.dependency_overrides.pop(get_knowledge_model, None)
