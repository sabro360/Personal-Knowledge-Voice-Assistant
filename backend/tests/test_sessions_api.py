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


def test_get_session_returns_existing_session() -> None:
    """GET /sessions/{session_id} should return the session with HTTP 200."""
    created = client.post("/sessions").json()
    session_id = created["id"]

    response = client.get(f"/sessions/{session_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == session_id
    assert "started_at" in data


def test_get_session_returns_404_for_missing_id() -> None:
    """GET /sessions/{session_id} should return 404 when session does not exist."""
    response = client.get("/sessions/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"


def test_list_sessions_returns_200_with_sessions() -> None:
    """GET /sessions should return 200 with a list containing created sessions."""
    client.post("/sessions")

    response = client.get("/sessions")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "id" in data[0]
    assert "started_at" in data[0]


def test_list_sessions_returns_200_as_list() -> None:
    """GET /sessions should return 200 and a JSON array."""
    response = client.get("/sessions")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
