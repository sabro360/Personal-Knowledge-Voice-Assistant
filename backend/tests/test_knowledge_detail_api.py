from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_knowledge_returns_200_with_correct_data() -> None:
    """GET /knowledge/{id} should return 200 with the matching knowledge item."""
    session = client.post("/sessions").json()
    knowledge = client.post(f"/sessions/{session['id']}/knowledge").json()

    response = client.get(f"/knowledge/{knowledge['id']}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == knowledge["id"]
    assert data["session_id"] == session["id"]


def test_get_knowledge_returns_404_for_nonexistent_id() -> None:
    """GET /knowledge/{id} should return 404 when the knowledge item does not exist."""
    response = client.get("/knowledge/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Knowledge not found"
