from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_knowledge_returns_200_as_list() -> None:
    """GET /knowledge should return 200 with a JSON array."""
    response = client.get("/knowledge")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_knowledge_includes_created_knowledge() -> None:
    """GET /knowledge should include a Knowledge item created via POST /sessions/{id}/knowledge."""
    session = client.post("/sessions").json()
    knowledge = client.post(f"/sessions/{session['id']}/knowledge").json()[0]

    response = client.get("/knowledge")

    assert response.status_code == 200
    ids = [item["id"] for item in response.json()]
    assert knowledge["id"] in ids
