"""
Restaurant Agent — tìm quán ăn theo ngữ cảnh và danh sách món ăn.
"""
import sys
import json

from models.schemas import UserContext
from services import llm
from tools import to_gemini_tools, executor
from prompt.builder import build_system_prompt


async def run(context: UserContext, food_names: list[str], user_query: str | None = None) -> dict:
    """
    Trả về: { "restaurants": list[Restaurant dict] }
    Hoặc:   { "ask": True, "field": str, "message": str }
    """
    system = build_system_prompt(context)
    user_msg = _build_restaurant_request(context, food_names, user_query)
    messages = [{"role": "user", "content": user_msg}]

    max_iterations = 5
    found_restaurants: list[dict] = []

    for _ in range(max_iterations):
        try:
            response = await llm.call(
                system=system,
                messages=messages,
                tools=to_gemini_tools(["search_nearby_restaurants", "get_restaurant_detail", "rank_restaurants", "ask_user_for_context", "crawl_restaurant_reviews"]),
            )
        except Exception as e:
            print(f"[ERROR] Restaurant agent LLM call failed: {e}", file=sys.stderr)
            return {"restaurants": []}

        fc_parts = []
        text_parts = []

        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.function_call:
                    fc_parts.append(part.function_call)
                elif part.text:
                    text_parts.append(part.text)

        if not fc_parts:
            break

        tool_results = []
        ask_result = None

        for fc in fc_parts:
            tool_name = fc.name
            tool_input = dict(fc.args) if fc.args else {}

            result = await executor.execute(tool_name, tool_input)

            if result.get("ask"):
                ask_result = result
                break

            if tool_name in ("rank_restaurants", "search_nearby_restaurants"):
                if "restaurants" in result:
                    found_restaurants = result["restaurants"]

            tool_results.append({
                "tool_name": tool_name,
                "result": json.dumps(result, ensure_ascii=False),
            })

        if ask_result:
            return ask_result

        results_text = "\n".join(f"Kết quả {tr['tool_name']}: {tr['result']}" for tr in tool_results)
        messages.append({"role": "assistant", "content": "[Tool calls executed]"})
        messages.append({
            "role": "user",
            "content": f"Tool results:\n{results_text}\n\nHãy xếp hạng và gợi ý quán phù hợp nhất.",
        })

    return {"restaurants": found_restaurants}


def _build_restaurant_request(context: UserContext, food_names: list[str], user_query: str | None = None) -> str:
    parts = ["Hãy tìm quán ăn gần tôi."]
    if user_query:
        parts.append(f"Yêu cầu gốc của người dùng: {user_query}.")
    if food_names:
        parts.append(f"Tôi muốn ăn: {', '.join(food_names)}.")
    if context.location:
        parts.append(f"Vị trí của tôi: lat={context.location.lat}, lng={context.location.lng}.")
    else:
        parts.append("Tôi chưa cung cấp vị trí.")
    if context.budget:
        parts.append(f"Ngân sách: khoảng {context.budget:,} VND mỗi người.")
    if context.people:
        parts.append(f"Có {context.people} người.")
    return " ".join(parts)
