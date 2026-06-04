import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from models.schemas import UserContext, Location, Message
from agents import food_agent, restaurant_agent, orchestrator

# A simple mock Gemini candidate structure
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
async def test_food_agent_direct_text(mock_call):
    # Food agent parses json from direct text response
    mock_call.return_value = create_mock_llm_response(
        text='[{"name": "Bún chả", "category": "Bún", "description": "Ngon", "estimated_price": 50000, "reason": "Thèm", "tags": ["bún"]}]'
    )
    
    context = UserContext(
        location=Location(lat=10.77, lng=106.70, address="Q1"),
        budget=60000,
        meal_time="lunch"
    )
    
    res = await food_agent.run(context)
    assert "foods" in res
    assert len(res["foods"]) == 1
    assert res["foods"][0]["name"] == "Bún chả"
    assert res["food_names"] == ["Bún chả"]

@pytest.mark.asyncio
@patch("services.llm.call")
async def test_food_agent_ask_user(mock_call):
    # Food agent invokes ask_user_for_context
    fc = {
        "name": "ask_user_for_context",
        "args": {"field": "budget", "message": "Bạn muốn ăn bao nhiêu tiền?"}
    }
    mock_call.return_value = create_mock_llm_response(function_calls=[fc])
    
    context = UserContext(
        location=Location(lat=10.77, lng=106.70),
        meal_time="lunch"
    )
    
    res = await food_agent.run(context)
    assert res.get("ask") is True
    assert res.get("field") == "budget"
    assert "bao nhiêu tiền" in res.get("message")

@pytest.mark.asyncio
@patch("services.llm.call")
async def test_restaurant_agent_success(mock_call):
    # Restaurant agent call search_nearby_restaurants
    fc = {
        "name": "search_nearby_restaurants",
        "args": {"lat": 10.77, "lng": 106.70, "query": "Cơm tấm"}
    }
    # First response calls tool, second response ends
    mock_call.side_effect = [
        create_mock_llm_response(function_calls=[fc]),
        create_mock_llm_response(text="Xong")
    ]
    
    context = UserContext(
        location=Location(lat=10.77, lng=106.70),
        budget=60000
    )
    
    with patch("tools.executor.execute", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = {
            "restaurants": [{"name": "Cơm Tấm ngon", "score": 0.9}]
        }
        res = await restaurant_agent.run(context, ["Cơm tấm"])
        assert "restaurants" in res
        assert len(res["restaurants"]) == 1
        assert res["restaurants"][0]["name"] == "Cơm Tấm ngon"

@pytest.mark.asyncio
async def test_orchestrator_mock_mode():
    events = []
    async def callback(event: str, data: dict):
        events.append((event, data))
        
    messages = [Message(role="user", content="Tôi muốn ăn bún chả")]
    context = UserContext(
        location=Location(lat=10.77, lng=106.70),
        budget=80000
    )
    
    # Force mock mode
    with patch("agents.orchestrator.MOCK_MODE", True):
        await orchestrator.run(messages, context, callback)
        
    # Check if correct events are streamed
    event_names = [e[0] for e in events]
    assert "thinking" in event_names
    assert "food_results" in event_names
    assert "restaurant_results" in event_names
    assert "text" in event_names
    assert "done" in event_names

@pytest.mark.asyncio
async def test_orchestrator_mock_food_parsing():
    test_cases = {
        "Tôi muốn ăn cơm gà thì tìm quán nào gần đây cho tôi": "Cơm gà",
        "Tôi muốn ăn cơm gà\u00a0thì\u00a0tìm quán nào gần đây": "Cơm gà",
        "tôi muốn ăn    bún bò    ở  quán  nào ngon": "Bún bò",
        "muốn ăn cơm gà. Thì tìm quán nào": "Cơm gà",
        "ĂN PHỞ BÒ Ở ĐÂU": "Phở bò",
        "gợi ý món bánh canh cua ngon": "Bánh canh cua",
        "chỗ nào bán hủ tiếu Nam Vang gần đây": "Hủ tiếu",
        "Muốn ăn bánh xèo tại Sài Gòn": "Bánh xèo",
    }
    for q, expected in test_cases.items():
        events = []
        async def callback(event: str, data: dict):
            events.append((event, data))
            
        messages = [Message(role="user", content=q)]
        context = UserContext(
            location=Location(lat=10.77, lng=106.70),
            budget=80000
        )
        
        with patch("agents.orchestrator.MOCK_MODE", True):
            await orchestrator.run(messages, context, callback)
            
        food_results = next(data for event, data in events if event == "food_results")
        assert len(food_results["foods"]) == 1
        assert food_results["foods"][0]["name"] == expected, f"Failed for query: {q!r}"


@pytest.mark.asyncio
@patch("services.llm.call")
async def test_food_agent_fallback_when_llm_prints_tool_code(mock_call):
    """Gemini in <tool_code> thay vì function_call → gọi search trực tiếp."""
    mock_call.return_value = create_mock_llm_response(
        text=(
            "Chào bạn! Mình sẽ tìm món cay nhé!\n"
            "<tool_code>print(search_food_by_criteria(meal_time='lunch', preference='spicy'))</tool_code>"
        )
    )
    context = UserContext(meal_time="lunch", preferences=["cay"])

    with patch("tools.executor.execute", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = {
            "foods": [{
                "name": "Bún bò Huế",
                "category": "Bún",
                "description": "Cay nồng",
                "estimated_price": 55000,
                "reason": "Hợp khẩu vị cay",
                "tags": ["cay"],
            }]
        }
        res = await food_agent.run(context, "tôi mốn tìm món ăn cay")

    mock_exec.assert_called_once()
    assert mock_exec.call_args[0][0] == "search_food_by_criteria"
    assert res["food_names"] == ["Bún bò Huế"]


def test_strip_tool_artifacts():
    raw = (
        "Chào bạn!\n"
        "<tool_code>print(search_food_by_criteria(meal_time='lunch', preference='spicy'))</tool_code>\n"
        "Món cay ngon nhé."
    )
    cleaned = orchestrator._strip_tool_artifacts(raw)
    assert "<tool_code>" not in cleaned
    assert "search_food_by_criteria" not in cleaned
    assert "Chào bạn!" in cleaned
    assert "Món cay ngon nhé." in cleaned
