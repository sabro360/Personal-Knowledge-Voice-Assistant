from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_knowledge_graph_returns_200() -> None:
    """GET /knowledge/graph should return 200 with nodes and edges keys."""
    response = client.get("/knowledge/graph")

    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert isinstance(data["nodes"], list)
    assert isinstance(data["edges"], list)


def test_get_knowledge_graph_nodes_include_created_knowledge() -> None:
    """GET /knowledge/graph nodes should include Knowledge created via POST /sessions/{id}/knowledge."""
    session = client.post("/sessions").json()
    client.post(f"/sessions/{session['id']}/utterances", json={"speaker": "user", "text": "test"})
    knowledge = client.post(f"/sessions/{session['id']}/knowledge").json()[0]

    response = client.get("/knowledge/graph")

    assert response.status_code == 200
    node_ids = [node["id"] for node in response.json()["nodes"]]
    assert knowledge["id"] in node_ids


def test_get_knowledge_graph_edges_are_empty_on_sqlite() -> None:
    """GET /knowledge/graph edges should be empty on SQLite (no pgvector similarity)."""
    response = client.get("/knowledge/graph")

    assert response.status_code == 200
    # On SQLite, find_similar() always returns [] so no relations are auto-generated
    assert response.json()["edges"] == []
