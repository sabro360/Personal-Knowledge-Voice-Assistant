import pytest
from fastapi.testclient import TestClient

from app.api.sessions import get_knowledge_model
from app.main import app
from app.providers.dummy_knowledge_model import DummyKnowledgeModel
from app.providers.errors import KnowledgeExtractionError

client = TestClient(app)


@pytest.fixture(autouse=True)
def use_dummy_model():
    """Override the knowledge model dependency with DummyKnowledgeModel for all tests."""
    app.dependency_overrides[get_knowledge_model] = lambda: DummyKnowledgeModel()
    yield
    app.dependency_overrides.pop(get_knowledge_model, None)


def test_generate_knowledge_returns_201() -> None:
    """POST /sessions/{session_id}/knowledge should return 201 with knowledge data."""
    session = client.post("/sessions").json()

    response = client.post(f"/sessions/{session['id']}/knowledge")

    assert response.status_code == 201
    data = response.json()
    assert isinstance(data["id"], int)
    assert data["session_id"] == session["id"]
    assert data["title"] == "dummy title"
    assert data["summary"] == "dummy summary"
    assert data["question"] == "dummy question"
    assert data["category"] == "dummy category"
    assert "created_at" in data
    assert "updated_at" in data


def test_generate_knowledge_returns_404_for_missing_session() -> None:
    """POST /sessions/{session_id}/knowledge should return 404 when session does not exist."""
    response = client.post("/sessions/99999/knowledge")

    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"


def test_generate_knowledge_returns_502_on_extraction_error() -> None:
    """POST /sessions/{session_id}/knowledge should return 502 when extraction fails."""

    class FailingModel:
        def summarize_conversation(self, utterances):
            raise KnowledgeExtractionError("fail")

        def extract_questions(self, utterances):
            raise KnowledgeExtractionError("fail")

        def extract_keywords(self, utterances):
            raise KnowledgeExtractionError("fail")

        def classify_category(self, utterances):
            raise KnowledgeExtractionError("fail")

        def generate_title(self, utterances):
            raise KnowledgeExtractionError("fail")

    app.dependency_overrides[get_knowledge_model] = lambda: FailingModel()
    session = client.post("/sessions").json()

    response = client.post(f"/sessions/{session['id']}/knowledge")

    assert response.status_code == 502
    assert response.json()["detail"] == "Knowledge extraction failed"


def test_finish_session_succeeds_even_if_knowledge_extraction_fails() -> None:
    """POST /sessions/{session_id}/finish should return 200 even when knowledge extraction fails."""

    class FailingModel:
        def summarize_conversation(self, utterances):
            raise KnowledgeExtractionError("fail")

        def extract_questions(self, utterances):
            raise KnowledgeExtractionError("fail")

        def extract_keywords(self, utterances):
            raise KnowledgeExtractionError("fail")

        def classify_category(self, utterances):
            raise KnowledgeExtractionError("fail")

        def generate_title(self, utterances):
            raise KnowledgeExtractionError("fail")

    app.dependency_overrides[get_knowledge_model] = lambda: FailingModel()
    session = client.post("/sessions").json()

    response = client.post(f"/sessions/{session['id']}/finish")

    assert response.status_code == 200
    assert response.json()["ended_at"] is not None
