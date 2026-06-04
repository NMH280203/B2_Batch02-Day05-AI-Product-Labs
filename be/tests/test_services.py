import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from services import weather as weather_service
from services import places as places_service
from services import llm as llm_service

# ──────────────────────────────────────────────────────────────────────
# 1. Test Weather Service
# ──────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_weather_service_no_key():
    # Test fallback khi khong co key
    with patch("services.weather.OPENWEATHER_KEY", ""):
        res = await weather_service.get_weather(10.7769, 106.7009)
        assert res["condition"] == "normal"
        assert res["temp_c"] == 30.0

@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_weather_service_success(mock_get):
    # Mock OpenWeatherMap response
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json = MagicMock(return_value={
        "main": {"temp": 33.5},
        "weather": [{"id": 800, "description": "bầu trời quang đãng"}]
    })
    mock_get.return_value = mock_resp

    with patch("services.weather.OPENWEATHER_KEY", "dummy_key"):
        res = await weather_service.get_weather(10.7769, 106.7009)
        assert res["condition"] == "hot"
        assert res["temp_c"] == 33.5
        assert res["description"] == "bầu trời quang đãng"

@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_weather_service_rainy(mock_get):
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json = MagicMock(return_value={
        "main": {"temp": 24.0},
        "weather": [{"id": 501, "description": "mưa vừa"}]
    })
    mock_get.return_value = mock_resp

    with patch("services.weather.OPENWEATHER_KEY", "dummy_key"):
        res = await weather_service.get_weather(10.7769, 106.7009)
        assert res["condition"] == "rainy"
        assert res["temp_c"] == 24.0

@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_weather_service_cold(mock_get):
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json = MagicMock(return_value={
        "main": {"temp": 18.0},
        "weather": [{"id": 801, "description": "ít mây"}]
    })
    mock_get.return_value = mock_resp

    with patch("services.weather.OPENWEATHER_KEY", "dummy_key"):
        res = await weather_service.get_weather(10.7769, 106.7009)
        assert res["condition"] == "cold"
        assert res["temp_c"] == 18.0

@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_weather_service_error_fallback(mock_get):
    mock_get.side_effect = Exception("API error")
    with patch("services.weather.OPENWEATHER_KEY", "dummy_key"):
        res = await weather_service.get_weather(10.7769, 106.7009)
        assert res["condition"] == "normal"
        assert res["temp_c"] == 30.0


# ──────────────────────────────────────────────────────────────────────
# 2. Test Places Service
# ──────────────────────────────────────────────────────────────────────

def test_distance_calculation():
    # Khoang cach giua Ha Noi va TP.HCM khoang 1130-1160km
    d = places_service._calc_distance(21.0285, 105.8542, 10.7769, 106.7009)
    assert 1100 < d < 1200
    # Cung toa do = 0
    assert places_service._calc_distance(10.7769, 106.7009, 10.7769, 106.7009) == 0.0

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_places_search_mock(mock_post):
    # Test fallback to mock data when network fails or returns empty
    mock_post.side_effect = Exception("OSM network error")
    res = await places_service.search(10.7769, 106.7009, "cơm tấm")
    assert len(res) == 12
    assert res[0]["place_id"] == "mock_001"
    assert "Thuận Kiều" in res[0]["name"]

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_places_search_real_api(mock_post):
    # Mock Overpass elements response
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json = MagicMock(return_value={
        "elements": [
            {
                "type": "node",
                "id": 12345,
                "lat": 21.03,
                "lon": 105.80,
                "tags": {
                    "name": "Bún chả Sinh Từ",
                    "amenity": "restaurant",
                    "addr:street": "Nguyen Phong Sac",
                    "addr:housenumber": "123"
                }
            }
        ]
    })
    mock_post.return_value = mock_resp

    res = await places_service.search(21.03, 105.80, "bún chả", budget=150000)
    assert len(res) == 1
    assert res[0]["place_id"] == "osm_12345"
    assert res[0]["name"] == "Bún chả Sinh Từ"
    assert res[0]["rating"] == 4.2
    assert "123 Nguyen Phong Sac" in res[0]["address"]

@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_places_detail_api(mock_post):
    # Mock Overpass detail response
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json = MagicMock(return_value={
        "elements": [
            {
                "type": "node",
                "id": 12345,
                "lat": 21.03,
                "lon": 105.80,
                "tags": {
                    "name": "Bún chả Sinh Từ",
                    "amenity": "restaurant",
                    "addr:street": "Nguyen Phong Sac",
                    "addr:housenumber": "123"
                }
            }
        ]
    })
    mock_post.return_value = mock_resp

    res = await places_service.detail("osm_12345")
    assert res is not None
    assert res["name"] == "Bún chả Sinh Từ"
    assert res["formatted_address"] == "123 Nguyen Phong Sac"


# ──────────────────────────────────────────────────────────────────────
# 3. Test LLM Service
# ──────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_llm_service_mock_mode():
    with patch("services.llm.MOCK_MODE", True):
        # Test call
        res = await llm_service.call("system", [{"role": "user", "content": "hi"}])
        assert "mệt" in res.text or "bún" in res.text.lower()
        
        # Test stream
        stream = await llm_service.call("system", [{"role": "user", "content": "hi"}], stream=True)
        chunks = [chunk.text for chunk in stream]
        assert len(chunks) > 0
        
        # Test call_json
        json_res = await llm_service.call_json("system", "prompt")
        assert "foods" in json_res
        assert len(json_res["foods"]) > 0

# ──────────────────────────────────────────────────────────────────────
# 4. Test Scraper Service
# ──────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_scraper_service_trending_foods():
    from services import scraper
    res = await scraper.crawl_trending_foods("bánh mì")
    assert res["query"] == "bánh mì"
    assert len(res["results"]) > 0
    assert "source" in res

@pytest.mark.asyncio
async def test_scraper_service_restaurant_reviews():
    from services import scraper
    res = await scraper.crawl_restaurant_reviews("Thuận Kiều")
    assert res["restaurant"] == "Thuận Kiều"
    assert len(res["reviews"]) > 0
    assert "source" in res
