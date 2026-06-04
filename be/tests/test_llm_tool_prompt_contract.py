import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents import food_agent, orchestrator
from models.schemas import Location, Message, UserContext


def make_llm_response(text: str = "", function_calls: list[dict] | None = None):
    parts = []
    if text:
        part = MagicMock()
        part.text = text
        part.function_call = None
        parts.append(part)

    for fc in function_calls or []:
        part = MagicMock()
        part.text = None
        part.function_call = MagicMock()
        part.function_call.name = fc["name"]
        part.function_call.args = fc.get("args", {})
        parts.append(part)

    candidate = MagicMock()
    candidate.content.parts = parts

    response = MagicMock()
    response.candidates = [candidate]
    response.text = text
    return response


class TextChunk:
    def __init__(self, text: str):
        self.text = text


@pytest.mark.asyncio
@patch("services.llm.call", new_callable=AsyncMock)
async def test_food_prompt_calls_weather_tool_and_returns_food_output(mock_llm_call):
    user_query = "Trời mưa lạnh, tôi muốn món nóng dưới 80k, không cay quá."
    context = UserContext(
        location=Location(lat=10.7769, lng=106.7009, address="Q1"),
        budget=80000,
        preferences=["nóng"],
    )

    mock_llm_call.side_effect = [
        make_llm_response(
            function_calls=[
                {"name": "get_weather", "args": {"lat": 10.7769, "lng": 106.7009}}
            ]
        ),
        make_llm_response(
            text=json.dumps(
                [
                    {
                        "name": "Cháo gà hành gừng",
                        "category": "Cháo",
                        "description": "Ấm bụng, dễ ăn trong ngày mưa lạnh.",
                        "estimated_price": 45000,
                        "reason": "Phù hợp thời tiết lạnh và ngân sách dưới 80k.",
                        "tags": ["nóng", "ấm bụng"],
                    }
                ],
                ensure_ascii=False,
            )
        ),
    ]

    with patch("tools.executor.execute", new_callable=AsyncMock) as mock_execute:
        mock_execute.return_value = {
            "condition": "rainy",
            "temp_c": 22.0,
            "description": "Mưa nhẹ",
        }

        result = await food_agent.run(context, user_query)

    first_prompt = mock_llm_call.call_args_list[0].kwargs["messages"][0]["content"]
    assert user_query in first_prompt
    mock_execute.assert_called_once_with(
        "get_weather", {"lat": 10.7769, "lng": 106.7009}
    )
    assert result["foods"][0]["name"] == "Cháo gà hành gừng"
    assert result["foods"][0]["estimated_price"] <= 80000
    assert "nóng" in result["foods"][0]["tags"]


@pytest.mark.asyncio
@patch("services.llm.call", new_callable=AsyncMock)
async def test_orchestrator_real_prompt_routes_tools_and_streams_expected_events(mock_llm_call):
    user_query = (
        "Gợi ý món ăn tối dưới 80k cho 2 người đi hẹn hò, dị ứng đậu phộng, "
        "rồi tìm quán gần tôi."
    )
    messages = [Message(role="user", content=user_query)]
    context = UserContext(location=Location(lat=10.7769, lng=106.7009, address="Q1"))

    food = {
        "name": "Bún bò ít cay",
        "category": "Bún",
        "description": "Nước dùng nóng, có thể dặn không đậu phộng.",
        "estimated_price": 70000,
        "reason": "Hợp bữa tối, đi 2 người và vẫn trong ngân sách.",
        "tags": ["nóng", "date"],
    }
    restaurant = {
        "place_id": "test_place_1",
        "name": "Bún Bò Góc Nhỏ",
        "address": "12 Lê Lợi, Q1",
        "distance_km": 0.4,
        "rating": 4.5,
        "price_level": 2,
        "is_open": True,
        "maps_url": "https://maps.google.com/?q=test_place_1",
        "photo_url": None,
        "featured_dishes": ["Bún bò ít cay"],
        "score": 0.92,
    }

    mock_llm_call.side_effect = [
        make_llm_response(
            function_calls=[
                {
                    "name": "detect_intent",
                    "args": {
                        "intent": "food_and_restaurant",
                        "confidence": 0.96,
                        "missing_context": [],
                    },
                }
            ]
        ),
        make_llm_response(
            function_calls=[
                {
                    "name": "search_food_by_criteria",
                    "args": {
                        "weather": "normal",
                        "budget": 80000,
                        "preferences": ["date", "nóng"],
                        "allergies": ["dau phong"],
                        "purpose": "date",
                    },
                }
            ]
        ),
        make_llm_response(text=json.dumps([food], ensure_ascii=False)),
        make_llm_response(
            function_calls=[
                {
                    "name": "search_nearby_restaurants",
                    "args": {
                        "lat": 10.7769,
                        "lng": 106.7009,
                        "query": "Bún bò ít cay",
                        "budget": 80000,
                        "radius": 2000,
                    },
                }
            ]
        ),
        make_llm_response(text="Đã có danh sách quán phù hợp."),
        [TextChunk("Mình gợi ý Bún bò ít cay và quán Bún Bò Góc Nhỏ.")],
    ]

    async def execute_side_effect(tool_name: str, tool_input: dict):
        if tool_name == "search_food_by_criteria":
            return {"foods": [food], "food_names": [food["name"]]}
        if tool_name == "search_nearby_restaurants":
            return {"restaurants": [restaurant]}
        return {}

    events: list[tuple[str, dict]] = []

    async def stream_callback(event: str, data: dict):
        events.append((event, data))

    with patch("agents.orchestrator.MOCK_MODE", False), patch(
        "tools.executor.execute", new_callable=AsyncMock
    ) as mock_execute:
        mock_execute.side_effect = execute_side_effect

        await orchestrator.run(messages, context, stream_callback)

    food_agent_call = mock_llm_call.call_args_list[1].kwargs
    assert user_query in food_agent_call["messages"][0]["content"]
    assert "80,000" in food_agent_call["system"] or "80000" in food_agent_call["system"]
    assert "hẹn hò" in food_agent_call["system"] or "date" in food_agent_call["system"]
    assert "dau phong" in food_agent_call["system"] or "đậu phộng" in food_agent_call["system"]

    mock_execute.assert_any_call(
        "search_food_by_criteria",
        {
            "weather": "normal",
            "budget": 80000,
            "preferences": ["date", "nóng"],
            "allergies": ["dau phong"],
            "purpose": "date",
        },
    )
    mock_execute.assert_any_call(
        "search_nearby_restaurants",
        {
            "lat": 10.7769,
            "lng": 106.7009,
            "query": "Bún bò ít cay",
            "budget": 80000,
            "radius": 2000,
        },
    )

    event_names = [event for event, _ in events]
    assert "food_results" in event_names
    assert "restaurant_results" in event_names
    assert "text" in event_names
    assert event_names[-1] == "done"

    food_payload = next(data for event, data in events if event == "food_results")
    restaurant_payload = next(data for event, data in events if event == "restaurant_results")
    text_output = "".join(data["delta"] for event, data in events if event == "text")

    assert food_payload["foods"][0]["name"] == "Bún bò ít cay"
    assert restaurant_payload["restaurants"][0]["name"] == "Bún Bò Góc Nhỏ"
    assert "Bún bò ít cay" in text_output
