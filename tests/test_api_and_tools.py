import pytest
from fastapi.testclient import TestClient

from app import main
from app.tools import weekend_trip_cost

client = TestClient(main.app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "WeekendYatri" in data["message"]


def test_ask_endpoint_with_fake_llm(monkeypatch):
    def fake_ask_question(question: str, top_k: int = 5):
        return {
            "answer": f"Fake RAG itinerary for: {question} [1]",
            "citations": [
                {
                    "title": "Someshwar",
                    "source_url": "https://nashik.gov.in/en/tourism/places-of-interest/",
                    "page": None,
                }
            ],
            "retrieved_chunks": [
                {
                    "title": "Someshwar",
                    "district": "Nashik",
                    "category": "religious",
                    "content": "Destination: Someshwar",
                }
            ],
        }

    monkeypatch.setattr(main, "ask_question", fake_ask_question)

    response = client.post(
        "/ask",
        json={"question": "2-day trip to Nashik", "top_k": 3},
    )
    assert response.status_code == 200
    body = response.json()
    assert "Fake RAG itinerary" in body["answer"]
    assert len(body["citations"]) == 1
    assert body["citations"][0]["title"] == "Someshwar"
    assert len(body["retrieved_chunks"]) == 1


def test_weekend_trip_cost_own_car():
    result = weekend_trip_cost(
        round_trip_km=150,
        people=3,
        mode="own_car",
        stay_per_person=1000,
        food_per_person=500,
        mileage_kmpl=15,
        fuel_price_per_litre=105,
    )
    assert result["mode"] == "own_car"
    assert result["transport_cost"] == 1050.0
    assert result["stay_total"] == 3000.0
    assert result["food_total"] == 1500.0
    assert result["total_group_cost"] == 5550.0
    assert result["cost_per_person"] == 1850.0


def test_weekend_trip_cost_msrtc_bus():
    result = weekend_trip_cost(
        round_trip_km=100,
        people=2,
        mode="msrtc_bus",
        stay_per_person=500,
        food_per_person=300,
    )
    assert result["mode"] == "msrtc_bus"
    assert result["people"] == 2
    assert result["transport_cost"] > 0
    assert result["total_group_cost"] == round(
        result["transport_cost"] + 1000 + 600, 2
    )


def test_weekend_trip_cost_invalid_inputs():
    with pytest.raises(ValueError):
        weekend_trip_cost(
            round_trip_km=-10,
            people=2,
            mode="msrtc_bus",
        )

    with pytest.raises(ValueError):
        weekend_trip_cost(
            round_trip_km=100,
            people=2,
            mode="own_car",
        )