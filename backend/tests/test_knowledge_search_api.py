from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_search_knowledge_returns_200_with_list() -> None:
    """GET /knowledge/search?q=... should return 200 with a list."""
    response = client.get("/knowledge/search", params={"q": "test"})

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_search_knowledge_returns_empty_list_when_no_match() -> None:
    """GET /knowledge/search?q=... should return [] when nothing matches."""
    response = client.get("/knowledge/search", params={"q": "全く一致しないキーワードXYZ"})

    assert response.status_code == 200
    assert response.json() == []


def test_search_knowledge_returns_422_for_empty_query() -> None:
    """GET /knowledge/search?q= should return 422 (empty string not allowed)."""
    response = client.get("/knowledge/search", params={"q": ""})

    assert response.status_code == 422


def test_search_knowledge_returns_422_when_q_missing() -> None:
    """GET /knowledge/search without q should return 422."""
    response = client.get("/knowledge/search")

    assert response.status_code == 422
