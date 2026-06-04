from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents import food_agent, restaurant_agent


@dataclass
class Location:
    lat: float
    lng: float
    address: str | None = None


@dataclass
class UserContext:
    location: Location | None = None
    budget: int | None = None
    people: int | None = None
    meal_time: str | None = None
    purpose: str | None = None
    preferences: list[str] | None = None
    allergies: list[str] | None = None


class DummyPart:
    def __init__(self, text=None, function_call=None):
        self.text = text
        self.function_call = function_call


class DummyFunctionCall:
    def __init__(self, name, args=None):
        self.name = name
        self.args = args or {}


def create_mock_llm_response(*, text: str = "", function_calls=None):
    parts = []
    if text:
        parts.append(DummyPart(text=text))
    for fc in function_calls or []:
        parts.append(DummyPart(function_call=DummyFunctionCall(fc["name"], fc.get("args", {}))))
    candidate = MagicMock()
    candidate.content.parts = parts
    response = MagicMock()
    response.candidates = [candidate]
    return response


@pytest.mark.asyncio
@patch("services.llm.call", new_callable=AsyncMock)
async def test_food_prompt_cold_weather_prefers_warm_food(mock_call):
    mock_call.side_effect = [
        create_mock_llm_response(function_calls=[{"name": "get_weather", "args": {"lat": 10.7769, "lng": 106.7009}}]),
        create_mock_llm_response(
            text='{"foods":[{"name":"Lẩu thái chua cay","category":"Lẩu","description":"Nóng hổi cay nồng","estimated_price":80000,"reason":"Phù hợp trời lạnh","tags":["nóng","lẩu"]}]}'
        ),
    ]
    context = UserContext(location=Location(10.7769, 106.7009), meal_time="dinner", budget=100000)
    with patch("tools.executor.execute", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = {"condition": "cold", "temp_c": 15.0}
        result = await food_agent.run(context)
    assert result["foods"]
    assert result["foods"][0]["category"] == "Lẩu"
    mock_exec.assert_called_with("get_weather", {"lat": 10.7769, "lng": 106.7009})


@pytest.mark.asyncio
@patch("services.llm.call", new_callable=AsyncMock)
async def test_food_prompt_spicy_query_routes_fast(mock_call):
    mock_call.side_effect = [
        create_mock_llm_response(function_calls=[{"name": "search_food_by_criteria", "args": {"query": "tôi cần ăn món cay", "spicy": True}}]),
        create_mock_llm_response(text='{"foods":[{"name":"Bún bò Huế","category":"Bún","description":"Cay nồng","estimated_price":60000,"reason":"Hợp món cay","tags":["cay","nóng"]}]}'),
    ]
    context = UserContext(location=Location(10.7769, 106.7009), meal_time="dinner", budget=100000, preferences=["cay"])
    with patch("tools.executor.execute", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = {"foods": [{"name": "Bún bò Huế", "category": "Bún", "estimated_price": 60000, "tags": ["cay"]}]}
        result = await food_agent.run(context, user_query="tôi cần ăn món cay")
    assert result["foods"][0]["name"] == "Bún bò Huế"
    mock_exec.assert_called_with("search_food_by_criteria", {"query": "tôi cần ăn món cay", "spicy": True})


@pytest.mark.asyncio
@patch("services.llm.call", new_callable=AsyncMock)
async def test_food_prompt_budget_under_limit(mock_call):
    mock_call.return_value = create_mock_llm_response(text='{"foods":[{"name":"Cơm tấm","category":"Món cơm","description":"Dễ ăn","estimated_price":45000,"reason":"Phù hợp","tags":["budget"]}]}')
    context = UserContext(location=Location(10.7769, 106.7009), meal_time="lunch", budget=50000)
    with patch("tools.executor.execute", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = {"foods": [{"name": "Cơm tấm", "estimated_price": 45000}]}
        result = await food_agent.run(context, user_query="gợi ý món dưới 50k")
    assert result["foods"][0]["estimated_price"] <= 50000
    mock_exec.assert_not_called()


@pytest.mark.asyncio
@patch("services.llm.call", new_callable=AsyncMock)
async def test_food_prompt_trending_uses_trending_tool(mock_call):
    mock_call.return_value = create_mock_llm_response(function_calls=[{"name": "crawl_trending_foods", "args": {"query": "trend ăn uống mới nhất"}}])
    context = UserContext(location=Location(10.7769, 106.7009), meal_time="lunch")
    with patch("tools.executor.execute", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = {"results": ["Bánh đồng xu phô mai", "Trà chanh giã tay"]}
        await food_agent.run(context, user_query="món hot trend hôm nay")
    mock_exec.assert_called_with("crawl_trending_foods", {"query": "trend ăn uống mới nhất"})


@pytest.mark.asyncio
@patch("services.llm.call", new_callable=AsyncMock)
async def test_restaurant_prompt_nearby_search_uses_location(mock_call):
    mock_call.return_value = create_mock_llm_response(function_calls=[{"name": "search_nearby_restaurants", "args": {"lat": 10.7769, "lng": 106.7009, "radius": 2000}}])
    context = UserContext(location=Location(10.7769, 106.7009, "Quận 1, TP.HCM"), budget=120000, people=2)
    with patch("tools.executor.execute", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = {"restaurants": [{"name": "Quán A", "distance": 350, "rating": 4.6}]}
        result = await restaurant_agent.run(context, ["phở", "bún bò"], user_query="Tìm quán ăn gần tôi")
    assert result["restaurants"][0]["name"] == "Quán A"
    mock_exec.assert_called_with("search_nearby_restaurants", {"lat": 10.7769, "lng": 106.7009, "radius": 2000})


@pytest.mark.asyncio
@patch("services.llm.call", new_callable=AsyncMock)
async def test_restaurant_prompt_missing_location_requests_clarification(mock_call):
    mock_call.return_value = create_mock_llm_response(function_calls=[{"name": "ask_user_for_context", "args": {"field": "location", "message": "Bạn đang ở đâu?"}}])
    result = await restaurant_agent.run(UserContext(location=None, budget=100000), ["bún chả"], user_query="Tìm quán bún chả gần tôi")
    assert result["ask"] is True
    assert result["field"] == "location"


@pytest.mark.asyncio
@patch("services.llm.call", new_callable=AsyncMock)
async def test_restaurant_prompt_accuracy_includes_food_budget_people(mock_call):
    mock_call.return_value = create_mock_llm_response(text='{"restaurants":[{"name":"Quán Phở Ngon","rating":4.8,"distance":250}]}')
    context = UserContext(location=Location(10.775, 106.701, "Q.1"), budget=90000, people=3)
    with patch("tools.executor.execute", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = {"restaurants": []}
        result = await restaurant_agent.run(context, ["phở", "bún bò"], user_query="Tìm quán gần tôi")
    assert result["restaurants"] == []
    mock_exec.assert_not_called()


@pytest.mark.asyncio
async def test_general_greeting_does_not_call_tools():
    context = UserContext(location=None)
    with patch("agents.orchestrator.food_agent.search_direct", new_callable=AsyncMock) as mock_search_direct, \
         patch("agents.orchestrator.llm.call", new_callable=AsyncMock) as mock_call:
        mock_call.return_value = create_mock_llm_response(text="Xin chào bạn! Mình có thể giúp gì?")
        async def cb(event, data):
            return None
        from agents import orchestrator
        await orchestrator.run([MagicMock(role="user", content="xin chào")], context, cb)
    mock_search_direct.assert_not_called()
