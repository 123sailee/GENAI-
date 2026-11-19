from fastapi.testclient import TestClient

from app.main import app
from app.smart_search import search_destinations

client = TestClient(app)


def test_smart_search_returns_matching_places():
    results = search_destinations("Nashik", top_n=5)
    assert isinstance(results, list)
    assert len(results) > 0
    assert "place" in results[0]
    assert "similarity_score" in results[0]


def test_search_endpoint_returns_expected_schema():
    response = client.get("/search", params={"q": "temple"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["query"] == "temple"
    assert payload["total_results"] == len(payload["results"])
    assert isinstance(payload["results"], list)