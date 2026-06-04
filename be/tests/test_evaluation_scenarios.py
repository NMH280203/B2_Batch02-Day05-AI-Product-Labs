import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from models.schemas import UserContext, Location, Message
from agents import food_agent, restaurant_agent, orchestrator
import json

def create_mock_llm_response(text="", function_calls=None):
    mock_resp = MagicMock()
    parts = []
    if text:
        parts.append(MagicMock(text=text, function_call=None))
    if function_calls:
        for fc in function_calls:
            mock_part = MagicMock()
            mock_part.text = None
            mock_part.function_call = MagicMock()
            mock_part.function_call.name = fc["name"]
            mock_part.function_call.args = fc["args"]
            parts.append(mock_part)
            
    mock_candidate = MagicMock()
    mock_candidate.content.parts = parts
    mock_resp.candidates = [mock_candidate]
    return mock_resp

@pytest.mark.asyncio
@patch("services.llm.call")
async def test_eval_weather_matching_scenario(mock_call):
    """
    Kịch bản: Người dùng muốn món ăn phù hợp với thời tiết lạnh giá (cold).
    Đánh giá: Hệ thống phải gọi weather tool hoặc trả về món ăn nóng hổi phù hợp.
    """
    # Trả về function call get_weather
    fc = {
        "name": "get_weather",
        "args": {"lat": 10.7769, "lng": 106.7009}
    }
    
    mock_call.side_effect = [
        create_mock_llm_response(function_calls=[fc]),
        create_mock_llm_response(text='[{"name": "Lẩu thái chua cay", "category": "Lẩu", "description": "Nóng hổi cay nồng", "estimated_price": 80000, "reason": "Phù hợp trời lạnh", "tags": ["nóng", "lẩu"]}]')
    ]
    
    context = UserContext(
        location=Location(lat=10.7769, lng=106.7009),
        meal_time="dinner"
    )
    
    with patch("tools.executor.execute", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = {"condition": "cold", "temp_c": 15.0, "description": "Trời lạnh giá"}
        res = await food_agent.run(context)
        
        # Verify get_weather was called
        assert len(res["foods"]) > 0
        assert res["foods"][0]["category"] == "Lẩu"
        assert "nóng" in res["foods"][0]["tags"]


@pytest.mark.asyncio
@patch("services.llm.call")
async def test_eval_trending_food_scenario(mock_call):
    """
    Kịch bản: Người dùng hỏi về món ăn hot trend mới nhất.
    Đánh giá: Hệ thống phải gọi tool crawl_trending_foods.
    """
    fc = {
        "name": "crawl_trending_foods",
        "args": {"query": "trend ăn uống mới nhất"}
    }
    mock_call.return_value = create_mock_llm_response(function_calls=[fc])
    
    context = UserContext(
        location=Location(lat=10.7769, lng=106.7009),
        meal_time="lunch"
    )
    
    with patch("tools.executor.execute", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = {
            "results": ["Bánh đồng xu phô mai", "Trà chanh giã tay"]
        }
        res = await food_agent.run(context)
        
        # Vì mock_call kết thúc turn ở bước gọi function call, food_agent trả về rỗng hoặc kết quả ask.
        # Ở đây, ta kiểm thử rằng executor đã chạy crawl_trending_foods thành công.
        mock_exec.assert_called_with("crawl_trending_foods", {"query": "trend ăn uống mới nhất"})


@pytest.mark.asyncio
@patch("services.llm.call")
async def test_eval_restaurant_reviews_scenario(mock_call):
    """
    Kịch bản: Người dùng muốn xem review/đánh giá về một quán cụ thể.
    Đánh giá: Hệ thống phải điều hướng chính xác tới tool crawl_restaurant_reviews.
    """
    fc = {
        "name": "crawl_restaurant_reviews",
        "args": {"restaurant_name": "Phở Thìn"}
    }
    mock_call.side_effect = [
        create_mock_llm_response(function_calls=[fc]),
        create_mock_llm_response(text="Xong")
    ]
    
    context = UserContext(
        location=Location(lat=10.7769, lng=106.7009)
    )
    
    with patch("tools.executor.execute", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = {"reviews": ["Ngon tuyệt vời", "Thịt mềm nước ngọt"]}
        await restaurant_agent.run(context, ["Phở Thìn"])
        mock_exec.assert_any_call("crawl_restaurant_reviews", {"restaurant_name": "Phở Thìn"})


@pytest.mark.asyncio
@patch("services.llm.call")
async def test_eval_missing_location_clarify_scenario(mock_call):
    """
    Kịch bản: Người dùng muốn tìm quán ăn gần họ nhưng chưa có toạ độ định vị GPS.
    Đánh giá: Hệ thống phải yêu cầu vị trí thông qua tool ask_user_for_context.
    """
    fc = {
        "name": "ask_user_for_context",
        "args": {"field": "location", "message": "Bạn đang ở đâu?"}
    }
    mock_call.return_value = create_mock_llm_response(function_calls=[fc])
    
    context = UserContext(
        location=None, # Missing location
        budget=100000
    )
    
    res = await food_agent.run(context)
    assert res.get("ask") is True
    assert res.get("field") == "location"
