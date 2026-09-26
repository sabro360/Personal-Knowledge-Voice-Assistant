from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_full_conversation_flow() -> None:
    """Integration test: create session → add utterances → list utterances → finish session."""
    # 1. Session作成
    response = client.post("/sessions")
    assert response.status_code == 201
    session = response.json()
    session_id = session["id"]
    assert session["ended_at"] is None

    # 2. Utterance追加（user → assistant → user の3ターン）
    r1 = client.post(
        f"/sessions/{session_id}/utterances",
        json={"speaker": "user", "text": "なぜCDって虹色なの？"},
    )
    assert r1.status_code == 201
    assert r1.json()["sequence_number"] == 1

    r2 = client.post(
        f"/sessions/{session_id}/utterances",
        json={"speaker": "assistant", "text": "CDは回折格子として機能するためです"},
    )
    assert r2.status_code == 201
    assert r2.json()["sequence_number"] == 2

    r3 = client.post(
        f"/sessions/{session_id}/utterances",
        json={"speaker": "user", "text": "水滴の場合とは違う？"},
    )
    assert r3.status_code == 201
    assert r3.json()["sequence_number"] == 3

    # 3. Utterance取得（sequence_number 昇順で3件揃っていること）
    response = client.get(f"/sessions/{session_id}/utterances")
    assert response.status_code == 200
    utterances = response.json()
    assert len(utterances) == 3
    assert utterances[0]["speaker"] == "user"
    assert utterances[0]["sequence_number"] == 1
    assert utterances[1]["speaker"] == "assistant"
    assert utterances[1]["sequence_number"] == 2
    assert utterances[2]["speaker"] == "user"
    assert utterances[2]["sequence_number"] == 3

    # 4. Session終了
    response = client.post(f"/sessions/{session_id}/finish")
    assert response.status_code == 200
    finished = response.json()
    assert finished["id"] == session_id
    assert finished["ended_at"] is not None
