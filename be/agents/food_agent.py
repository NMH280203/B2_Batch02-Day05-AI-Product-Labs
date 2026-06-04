"""
Food Agent — tìm món ăn phù hợp dựa trên ngữ cảnh user.
Sử dụng google-genai SDK mới với function calling.
"""
import sys
import json
from datetime import datetime

from models.schemas import UserContext
from services import llm
from tools import to_gemini_tools, executor
from prompt.builder import build_system_prompt


async def run(context: UserContext, user_query: str | None = None) -> dict:
    """
    Chạy food agent.
    Trả về: { "foods": list[FoodSuggestion dict], "food_names": list[str] }
    Hoặc:   { "ask": True, "field": str, "message": str }
    """
    system = build_system_prompt(context)
    user_msg = _build_food_request(context, user_query)
    messages = [{"role": "user", "content": user_msg}]

    max_iterations = 5

    for _ in range(max_iterations):
        try:
            response = await llm.call(
                system=system,
                messages=messages,
                tools=to_gemini_tools(["get_weather", "search_food_by_criteria", "ask_user_for_context", "crawl_trending_foods"]),
            )
        except Exception as e:
            print(f"[ERROR] Food agent LLM call failed: {e}", file=sys.stderr)
            return {"foods": [], "food_names": []}

        # Kiểm tra function calls trong google-genai response
        fc_parts = []
        text_parts = []

        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.function_call:
                    fc_parts.append(part.function_call)
                elif part.text:
                    text_parts.append(part.text)

        if not fc_parts:
            # End turn — parse foods từ text
            full_text = "\n".join(text_parts)
            foods = _parse_foods_from_text(full_text)
            # Chỉ fallback khi model bỏ qua function_call (lần đầu) hoặc in <tool_code>
            first_turn = len(messages) == 1
            if _is_text_tool_call(full_text) or (first_turn and not foods):
                direct = await _direct_food_search(context, user_query)
                if direct["foods"]:
                    return direct
            food_names = [f["name"] for f in foods]
            return {"foods": foods, "food_names": food_names}

        # Xử lý function calls
        tool_results = []
        ask_result = None

        for fc in fc_parts:
            tool_name = fc.name
            tool_input = dict(fc.args) if fc.args else {}

            result = await executor.execute(tool_name, tool_input)

            if result.get("ask"):
                ask_result = result
                break

            tool_results.append({
                "tool_name": tool_name,
                "result": json.dumps(result, ensure_ascii=False),
            })

        if ask_result:
            return ask_result

        # Append kết quả vào messages
        results_text = "\n".join(
            f"Kết quả {tr['tool_name']}: {tr['result']}" for tr in tool_results
        )
        messages.append({"role": "assistant", "content": f"[Tool calls executed]"})
        messages.append({
            "role": "user",
            "content": f"Tool results:\n{results_text}\n\nBây giờ hãy gợi ý món ăn dựa trên kết quả trên bằng tiếng Việt. Nếu user hỏi món cay/spicy thì chỉ ưu tiên các món có tag, mô tả, hoặc tên thể hiện rõ độ cay/nóng.",
        })

    return {"foods": [], "food_names": []}


def _infer_meal_time() -> str:
    hour = datetime.now().hour
    if 5 <= hour < 10:
        return "breakfast"
    if 10 <= hour < 14:
        return "lunch"
    if 14 <= hour < 17:
        return "snack"
    return "dinner"


def _build_tool_input_from_context(
    context: UserContext,
    user_query: str | None = None,
) -> dict:
    normalized = (user_query or "").lower()
    weather = "normal"
    if any(w in normalized for w in ["nong", "nóng", "am", "mua", "mưa", "lanh", "lạnh"]):
        if any(w in normalized for w in ["mua", "mưa"]):
            weather = "rainy"
        elif any(w in normalized for w in ["lanh", "lạnh"]):
            weather = "cold"
        else:
            weather = "hot"

    spicy = any(w in normalized for w in ["cay", "spicy", "cay nồng", "cay nóng"])
    preferred_tags = []
    if spicy:
        preferred_tags.extend(["cay", "spicy", "nóng", "lẩu cay", "mì cay", "bún bò huế"])

    return {
        "meal_time": context.meal_time or _infer_meal_time(),
        "budget": context.budget or 80000,
        "preferences": list(context.preferences or []),
        "allergies": list(context.allergies or []),
        "weather": weather,
        "spicy": spicy,
        "preferred_tags": preferred_tags,
    }


def _is_text_tool_call(text: str) -> bool:
    lowered = text.lower()
    return (
        "<tool_code>" in lowered
        or "search_food_by_criteria(" in lowered
        or "crawl_trending_foods(" in lowered
    )


async def _direct_food_search(
    context: UserContext,
    user_query: str | None = None,
) -> dict:
    normalized = (user_query or "").lower()
    if any(k in normalized for k in ["trend", "hot", "xu huong", "xhuong", "thinh hanh"]):
        tool_name = "crawl_trending_foods"
        tool_input = {"query": user_query or "món ăn hot trend Việt Nam"}
    else:
        tool_name = "search_food_by_criteria"
        tool_input = _build_tool_input_from_context(context, user_query)
        tool_input["query"] = user_query or ""

    result = await executor.execute(tool_name, tool_input)
    if tool_name == "crawl_trending_foods":
        foods = []
        for idx, item in enumerate(result.get("results", [])[:5]):
            foods.append({
                "name": str(item)[:40],
                "category": "Hot Trend",
                "description": str(item),
                "estimated_price": 50000 + idx * 5000,
                "reason": "Dữ liệu cào thực tế từ internet.",
                "tags": ["hot trend"],
            })
    else:
        foods = result.get("foods", [])
        query = (user_query or "").lower()
        if any(k in query for k in ["cay", "spicy", "cay nồng", "cay nong"]):
            spicy_foods = [
                f for f in foods
                if any(tag in str(f.get("tags", [])).lower() for tag in ["cay", "spicy", "nóng", "hot"])
                or any(word in str(f.get("name", "")).lower() for word in ["cay", "huế", "mì cay", "lẩu cay"])
                or any(word in str(f.get("description", "")).lower() for word in ["cay", "spicy", "nóng"])
            ]
            if spicy_foods:
                foods = spicy_foods

    return {"foods": foods, "food_names": [f["name"] for f in foods]}


async def search_direct(
    context: UserContext,
    user_query: str | None = None,
) -> dict:
    """Gọi tool tìm món trực tiếp, bỏ qua LLM (fallback khi model in <tool_code>)."""
    return await _direct_food_search(context, user_query)


def _build_food_request(context: UserContext, user_query: str | None = None) -> str:
    parts = [
        "BẮT BUỘC: Gọi tool `search_food_by_criteria` hoặc `crawl_trending_foods` để tìm món ăn. "
        "TUYỆT ĐỐI KHÔNG tự nghĩ ra hoặc bịa đặt danh sách món ăn. "
        "Chỉ dùng kết quả trả về từ tool để gợi ý cho người dùng.",
        "QUY TẮC ƯU TIÊN: nếu user nói món cay / spicy / cay nồng / lẩu cay / mì cay / bún bò Huế / món nóng thì phải ưu tiên các món có tag hoặc mô tả liên quan đến cay/nóng. "
        "Không được trả các món trung tính như bánh mì, bánh cuốn, món nhạt nếu không có lý do rõ ràng.",
    ]
    if user_query:
        parts.append(f"Yêu cầu gốc của người dùng: {user_query}.")
    if context.meal_time:
        meal_map = {"breakfast": "bữa sáng", "lunch": "bữa trưa", "dinner": "bữa tối", "snack": "bữa nhẹ"}
        parts.append(f"Thời điểm: {meal_map.get(context.meal_time, 'bữa trưa')}.")
    if context.budget:
        parts.append(f"Ngân sách: khoảng {context.budget:,} VND.")
    if context.preferences:
        parts.append(f"Tôi thích: {', '.join(context.preferences)}.")
    if context.allergies:
        parts.append(f"Tôi không ăn được / dị ứng: {', '.join(context.allergies)}.")
    if context.location:
        parts.append(f"Vị trí: lat={context.location.lat}, lng={context.location.lng}.")
    return " ".join(parts)


def _parse_foods_from_text(text: str) -> list[dict]:
    """Cố parse JSON từ text response."""
    try:
        start = text.find("[")
        end = text.rfind("]") + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            data = json.loads(text[start:end])
            if "foods" in data:
                return data["foods"]
    except Exception:
        pass
    return []
