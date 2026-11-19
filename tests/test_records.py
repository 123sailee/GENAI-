from fastapi.testclient import TestClient

from app.main import app
from app.records import load_records

client = TestClient(app)


def test_load_records_not_empty():
    records = load_records()
    assert isinstance(records, list)
    assert len(records) > 0
    first = records[0]
    assert first.place
    assert first.district
    assert first.category
    assert first.best_season


def test_records_endpoint_returns_list():
    response = client.get("/records?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 5


def test_record_by_id_not_found():
    response = client.get("/records/999999")
    assert response.status_code == 404