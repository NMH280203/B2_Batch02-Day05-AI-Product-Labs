import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from tools.weather import tool as weather_handler
from tools.food_search import tool as food_handler
from tools.places import tool as places_handler
from tools.ranking import tool as ranking_handler

@pytest.mark.asyncio
async def test_weather_handler():
    with patch("services.weather.get_weather", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = {"condition": "hot", "temp_c": 35.0, "description": "Nóng bức"}
        res = await weather_handler.handle({"lat": 10.77, "lng": 106.70})
        assert res["condition"] == "hot"
        assert res["temp_c"] == 35.0
        mock_get.assert_called_once_with(10.77, 106.70)

@pytest.mark.asyncio
async def test_places_handler_search():
    with patch("services.places.search", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = [{"name": "Quán A"}]
        res = await places_handler.handle_search({"lat": 10.77, "lng": 106.70, "query": "bún", "budget": "50000"})
        assert res["restaurants"] == [{"name": "Quán A"}]
        mock_search.assert_called_once_with(10.77, 106.70, "bún", 2000, 50000)

@pytest.mark.asyncio
async def test_places_handler_detail():
    with patch("services.places.detail", new_callable=AsyncMock) as mock_detail:
        mock_detail.return_value = {"name": "Quán A"}
        res = await places_handler.handle_detail({"place_id": "abc"})
        assert res["detail"] == {"name": "Quán A"}
        mock_detail.assert_called_once_with("abc")

@pytest.mark.asyncio
async def test_food_search_handler_success():
    mock_food_res = {
        "foods": [
            {
                "name": "Phở bò",
                "category": "Phở",
                "description": "Ngon nóng hổi",
                "estimated_price": 50000,
                "reason": "Phù hợp trời lạnh",
                "tags": ["ấm", "truyền thống"]
            }
        ]
    }
    with patch("services.llm.call_json", new_callable=AsyncMock) as mock_call_json:
        mock_call_json.return_value = mock_food_res
        res = await food_handler.handle({
            "meal_time": "breakfast",
            "budget": 60000,
            "preferences": ["nước"],
            "allergies": [],
            "weather": "cold",
            "purpose": "solo"
        })
        assert len(res["foods"]) == 1
        assert res["foods"][0]["name"] == "Phở bò"

@pytest.mark.asyncio
async def test_food_search_handler_fallback():
    with patch("services.llm.call_json", new_callable=AsyncMock) as mock_call_json:
        mock_call_json.side_effect = Exception("LLM failure")
        res = await food_handler.handle({})
        # Fallback to empty list but handles error gracefully without crash
        assert "foods" in res
        assert "error" in res

@pytest.mark.asyncio
async def test_ranking_handler_empty():
    res = await ranking_handler.handle({"restaurants": [], "food_names": []})
    assert res == {"restaurants": []}

@pytest.mark.asyncio
async def test_ranking_handler_sorting():
    restaurants = [
        {
            "name": "Quán 1",
            "rating": 4.0,
            "distance_km": 1.5,
            "price_level": 2,
            "user_ratings_total": 50,
            "featured_dishes": ["Bún chả"]
        },
        {
            "name": "Quán 2",
            "rating": 4.8,
            "distance_km": 0.2,
            "price_level": 1,
            "user_ratings_total": 500,
            "featured_dishes": ["Bún chả", "Nem cua bể"]
        }
    ]
    
    # Quán 2 tốt hơn ở mọi khía cạnh: rating cao hơn, gần hơn (0.2km vs 1.5km), rẻ hơn (level 1 vs 2), nhiều review hơn (500 vs 50).
    res = await ranking_handler.handle({
        "restaurants": restaurants,
        "food_names": ["Bún chả"],
        "top_n": 5
    })
    
    ranked = res["restaurants"]
    assert len(ranked) == 2
    assert ranked[0]["name"] == "Quán 2"
    assert ranked[1]["name"] == "Quán 1"
    assert ranked[0]["score"] > ranked[1]["score"]

@pytest.mark.asyncio
async def test_crawl_trending_foods_executor():
    from tools import executor
    res = await executor.execute("crawl_trending_foods", {"query": "bánh mì"})
    assert res["query"] == "bánh mì"
    assert "results" in res

@pytest.mark.asyncio
async def test_crawl_restaurant_reviews_executor():
    from tools import executor
    res = await executor.execute("crawl_restaurant_reviews", {"restaurant_name": "Phở Gia Truyền"})
    assert res["restaurant"] == "Phở Gia Truyền"
    assert "reviews" in res


@pytest.mark.asyncio
async def test_weather_handler_invalid_coords():
    with patch("services.weather.get_weather", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = {"condition": "normal", "temp_c": 25.0, "description": "Bình thường"}
        
        # Test coordinates out of bounds (should fallback to default: 10.7769, 106.7009)
        await weather_handler.handle({"lat": 95.0, "lng": 200.0})
        mock_get.assert_called_with(10.7769, 106.7009)
        
        # Test invalid type coordinates (should fallback)
        await weather_handler.handle({"lat": "invalid", "lng": None})
        mock_get.assert_called_with(10.7769, 106.7009)


@pytest.mark.asyncio
async def test_places_handler_invalid_inputs():
    with patch("services.places.search", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = []
        
        # Test negative radius and invalid coordinates
        await places_handler.handle_search({
            "lat": -100.0,
            "lng": 250.0,
            "radius": -500,
            "budget": -1000
        })
        # Should fallback to default TP.HCM coordinates, radius=2000, and budget=None
        mock_search.assert_called_once_with(10.7769, 106.7009, "quán ăn", 2000, None)


@pytest.mark.asyncio
async def test_ranking_handler_invalid_inputs():
    # Test invalid top_n and invalid type of restaurants
    res = await ranking_handler.handle({
        "restaurants": "not a list",
        "top_n": -10
    })
    assert res == {"restaurants": []}
    
    # Test top_n <= 0 falling back to 5
    restaurants = [{"name": f"Quán {i}", "rating": 4.5} for i in range(10)]
    res2 = await ranking_handler.handle({
        "restaurants": restaurants,
        "food_names": ["Bún"],
        "top_n": 0
    })
    # Should fallback top_n to 5
    assert len(res2["restaurants"]) == 5


@pytest.mark.asyncio
async def test_food_search_handler_invalid_inputs():
    with patch("services.llm.call_json", new_callable=AsyncMock) as mock_call_json:
        mock_call_json.return_value = {"foods": []}
        
        # Test negative budget, invalid meal_time, invalid weather, and invalid purpose
        await food_handler.handle({
            "meal_time": "invalid_meal",
            "budget": -50000,
            "weather": "super_hot",
            "purpose": "party",
            "preferences": "not a list",
            "allergies": None
        })
        
        # Verify the call was handled. Since food_handler uses internal prompt building, 
        # let's assert that the handler successfully executed the call with fallback/defaulted variables.
        mock_call_json.assert_called_once()

