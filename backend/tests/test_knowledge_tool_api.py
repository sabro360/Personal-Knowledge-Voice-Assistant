from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app
from app.models.conversation_session import ConversationSession
from app.repositories.knowledge_repository import KnowledgeRepository

client = TestClient(app)


def _create_session_and_knowledge(title: str, summary: str) -> None:
    """Helper to create a session and one knowledge item via the app's DB."""
    from app.db.database import SessionLocal

    with SessionLocal() as db:
        cs = ConversationSession(started_at=datetime.now(timezone.utc))
        db.add(cs)
        db.flush()
        repo = KnowledgeRepository(db)
        repo.create(session_id=cs.id, title=title, summary=summary)
        db.commit()


def test_search_tool_returns_200_with_results() -> None:
    """POST /knowledge/search_tool should return 200 with matching results."""
    _create_session_and_knowledge(title="CDの虹色の仕組み", summary="光の回折")

    response = client.post("/knowledge/search_tool", json={"query": "CD"})

    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 1
    titles = [r["title"] for r in data["results"]]
    assert "CDの虹色の仕組み" in titles


def test_search_tool_returns_empty_when_no_match() -> None:
    """POST /knowledge/search_tool should return results=[] and count=0 when nothing matches."""
    response = client.post(
        "/knowledge/search_tool", json={"query": "全く関係ないキーワードXYZ999"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["results"] == []
    assert data["count"] == 0


def test_search_tool_returns_422_for_empty_query() -> None:
    """POST /knowledge/search_tool should return 422 when query is empty."""
    response = client.post("/knowledge/search_tool", json={"query": ""})

    assert response.status_code == 422


def test_search_tool_result_has_expected_fields() -> None:
    """POST /knowledge/search_tool response should contain results and count keys."""
    response = client.post("/knowledge/search_tool", json={"query": "test"})

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "count" in data
    assert isinstance(data["results"], list)
    assert isinstance(data["count"], int)
