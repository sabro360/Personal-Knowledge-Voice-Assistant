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


def test_add_utterance_returns_201() -> None:
    """POST /sessions/{session_id}/utterances should return 201 with utterance data."""
    session = client.post("/sessions").json()
    session_id = session["id"]

    response = client.post(
        f"/sessions/{session_id}/utterances",
        json={"speaker": "user", "text": "なぜCDって虹色なの？"},
    )

    assert response.status_code == 201
    data = response.json()
    assert isinstance(data["id"], int)
    assert data["session_id"] == session_id
    assert data["speaker"] == "user"
    assert data["text"] == "なぜCDって虹色なの？"
    assert "timestamp" in data
    assert data["sequence_number"] == 1


def test_add_utterance_increments_sequence_number() -> None:
    """sequence_number should increment with each utterance added."""
    session = client.post("/sessions").json()
    session_id = session["id"]

    first = client.post(
        f"/sessions/{session_id}/utterances",
        json={"speaker": "user", "text": "first"},
    ).json()
    second = client.post(
        f"/sessions/{session_id}/utterances",
        json={"speaker": "assistant", "text": "second"},
    ).json()

    assert first["sequence_number"] == 1
    assert second["sequence_number"] == 2


def test_add_utterance_returns_404_for_missing_session() -> None:
    """POST /sessions/{session_id}/utterances should return 404 for non-existent session."""
    response = client.post(
        "/sessions/99999/utterances",
        json={"speaker": "user", "text": "hello"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"


def test_list_utterances_returns_utterances_in_order() -> None:
    """GET /sessions/{session_id}/utterances should return utterances in sequence order."""
    session = client.post("/sessions").json()
    session_id = session["id"]
    client.post(f"/sessions/{session_id}/utterances", json={"speaker": "user", "text": "first"})
    client.post(f"/sessions/{session_id}/utterances", json={"speaker": "assistant", "text": "second"})

    response = client.get(f"/sessions/{session_id}/utterances")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["sequence_number"] == 1
    assert data[1]["sequence_number"] == 2
    assert data[0]["text"] == "first"


def test_list_utterances_returns_empty_list_for_session_with_no_utterances() -> None:
    """GET /sessions/{session_id}/utterances should return [] for a session with no utterances."""
    session = client.post("/sessions").json()
    session_id = session["id"]

    response = client.get(f"/sessions/{session_id}/utterances")

    assert response.status_code == 200
    assert response.json() == []


def test_list_utterances_returns_404_for_missing_session() -> None:
    """GET /sessions/{session_id}/utterances should return 404 for non-existent session."""
    response = client.get("/sessions/99999/utterances")

    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"


def test_finish_session_sets_ended_at() -> None:
    """POST /sessions/{session_id}/finish should return 200 with ended_at set."""
    session = client.post("/sessions").json()
    session_id = session["id"]

    response = client.post(f"/sessions/{session_id}/finish")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == session_id
    assert data["ended_at"] is not None


def test_finish_session_returns_404_for_missing_session() -> None:
    """POST /sessions/{session_id}/finish should return 404 for non-existent session."""
    response = client.post("/sessions/99999/finish")

    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"
