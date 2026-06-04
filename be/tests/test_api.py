import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_restaurants_endpoint():
    # Test using query params
    # Default mock mode or mock search
    with patch("services.places.search", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = [
            {
                "place_id": "test_id",
                "name": "Test Restaurant",
                "address": "123 Street",
                "distance_km": 0.5,
                "rating": 4.5,
                "price_level": 2,
                "is_open": True,
                "phone": "12345",
                "maps_url": "url",
                "photo_url": None,
                "featured_dishes": ["phở"],
                "score": 0.0
            }
        ]
        
        response = client.get("/api/restaurants?lat=10.77&lng=106.70&query=pho&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert "restaurants" in data
        assert len(data["restaurants"]) == 1
        assert data["restaurants"][0]["name"] == "Test Restaurant"
        assert data["total"] == 1
        assert data["query_used"] == "pho"

def test_chat_endpoint_mock():
    # Chat endpoint uses SSE. We can read the stream line by line.
    payload = {
        "messages": [{"role": "user", "content": "Tôi muốn ăn gì đó nhẹ nhàng"}],
        "context": {
            "location": {"lat": 10.77, "lng": 106.70, "address": "Q1"},
            "budget": 50000,
            "people": 1,
            "meal_time": "snack"
        }
    }
    
    with patch("agents.orchestrator.MOCK_MODE", True):
        response = client.post("/api/chat", json=payload)
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        
        # Read the lines to verify we get SSE events
        lines = []
        for line in response.iter_lines():
            if line:
                if isinstance(line, bytes):
                    lines.append(line.decode("utf-8"))
                else:
                    lines.append(line)
        
        assert len(lines) > 0
        assert any(l.startswith("event: thinking") for l in lines)
        assert any(l.startswith("event: food_results") for l in lines)
        assert any(l.startswith("event: done") for l in lines)
