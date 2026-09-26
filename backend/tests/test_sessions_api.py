from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_session_returns_201() -> None:
    """POST /sessions should return 201 with a valid session object."""
    response = client.post("/sessions")

    assert response.status_code == 201
    data = response.json()
    assert isinstance(data["id"], int)
    assert "started_at" in data
    assert data["ended_at"] is None
    assert data["title"] is None
    assert "created_at" in data
