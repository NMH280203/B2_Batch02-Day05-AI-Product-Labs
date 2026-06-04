"""
Orchestrator — điều phối toàn bộ flow.
Hỗ trợ MOCK_MODE khi không có GEMINI_API_KEY.
"""
import sys
import json
import re
import unicodedata
import asyncio
from typing import Callable, Awaitable

from models.schemas import UserContext, Message
from services import llm
from services.llm import MOCK_MODE, MOCK_FOOD_RESPONSE, MOCK_FINAL_TEXT, _MockStream
from tools import to_gemini_tools
from prompt.builder import build_system_prompt
from agents import food_agent, restaurant_agent


StreamCallback = Callable[[str, dict], Awaitable[None]]

_TOOL_CODE_RE = re.compile(
    r"<tool_code>.*?</tool_code>",
    re.IGNORECASE | re.DOTALL,
)
_FENCED_CODE_RE = re.compile(
    r"```(?:python|tool_code)?\s*.*?(?:search_food_by_criteria|crawl_trending_foods)\(.*?\)\s*```",
    re.IGNORECASE | re.DOTALL,
)


def _strip_tool_artifacts(text: str) -> str:
    """Loại bỏ pseudo tool calls mà Gemini in ra dạng text/code."""
    cleaned = _TOOL_CODE_RE.sub("", text)
    cleaned = _FENCED_CODE_RE.sub("", cleaned)
    cleaned = re.sub(
        r"^\s*(?:print\s*\()?search_food_by_criteria\s*\([^)]*\)\)?\s*$",
        "",
        cleaned,
        flags=re.IGNORECASE | re.MULTILINE,
    )
    return re.sub(r"\n{3,}", "\n\n", cleaned).strip()


async def _stream_llm_text(stream_callback: StreamCallback, stream) -> None:
    """Stream text từ LLM và lọc pseudo tool calls trước khi gửi cho user."""
    buffer = ""
    emitted_len = 0

    async def _consume(chunk) -> None:
        nonlocal buffer, emitted_len
        try:
            delta = chunk.text or ""
        except Exception:
            return
        if not delta:
            return
        buffer += delta
        cleaned = _strip_tool_artifacts(buffer)
        if len(cleaned) > emitted_len:
            await stream_callback("text", {"delta": cleaned[emitted_len:]})
            emitted_len = len(cleaned)

    if hasattr(stream, "__aiter__"):
        async for chunk in stream:
            await _consume(chunk)
    else:
        for chunk in stream:
            await _consume(chunk)

    tail = _strip_tool_artifacts(buffer)
    if len(tail) > emitted_len:
        await stream_callback("text", {"delta": tail[emitted_len:]})


def _normalize_text(text: str) -> str:
    lowered = text.lower()
    without_marks = "".join(
        ch for ch in unicodedata.normalize("NFD", lowered)
        if unicodedata.category(ch) != "Mn"
    )
    return without_marks.replace("đ", "d")


def _append_unique(items: list[str], value: str) -> None:
    if value and value not in items:
        items.append(value)


def _extract_budget(text: str) -> int | None:
    normalized = _normalize_text(text).replace(",", ".")
    compact = re.sub(r"(\d)\s+(\d{3})(\D|$)", r"\1\2\3", normalized)
    patterns = [
        r"(?:duoi|toi da|max|khoang|budget|ngan sach|tam)\s*(\d+(?:\.\d+)?)\s*(trieu|tr|m|k|nghin|ngan|vnd|d)?",
        r"(\d+(?:\.\d+)?)\s*(trieu|tr|m|k|nghin|ngan|vnd|d)\s*(?:tro xuong|moi nguoi|/nguoi)?",
    ]

    for pattern in patterns:
        match = re.search(pattern, compact)
        if not match:
            continue
        amount = float(match.group(1))
        unit = match.group(2) or ""
        if unit in {"trieu", "tr", "m"}:
            return int(amount * 1_000_000)
        if unit in {"k", "nghin", "ngan"} or amount < 1000:
            return int(amount * 1000)
        return int(amount)
    return None


def _enrich_context_from_messages(messages: list[Message], context: UserContext) -> str:
    last_user_msg = next((m.content for m in reversed(messages) if m.role == "user"), "")
    if not last_user_msg:
        return ""

    normalized = _normalize_text(last_user_msg)

    if not context.budget:
        budget = _extract_budget(last_user_msg)
        if budget:
            context.budget = budget

    if not context.people:
        people_match = re.search(r"(\d{1,2})\s*(?:nguoi|ban|pax)", normalized)
        if people_match:
            context.people = int(people_match.group(1))
        elif "mot minh" in normalized or "di 1 minh" in normalized:
            context.people = 1

    if not context.meal_time:
        meal_keywords = [
            ("breakfast", ["bua sang", "an sang", "diem tam"]),
            ("lunch", ["bua trua", "an trua"]),
            ("dinner", ["bua toi", "an toi", "bua dem"]),
            ("snack", ["an vat", "snack", "bua nhe", "xế", "xe chieu"]),
        ]
        for meal_time, keywords in meal_keywords:
            if any(keyword in normalized for keyword in keywords):
                context.meal_time = meal_time
                break

    if not context.purpose:
        purpose_keywords = [
            ("date", ["hen ho", "di hen", "date"]),
            ("family", ["gia dinh", "bo me", "tre em"]),
            ("friends", ["ban be", "nhom ban", "di choi"]),
            ("work", ["cong viec", "gap doi tac", "lam viec", "van phong"]),
            ("solo", ["mot minh", "solo"]),
        ]
        for purpose, keywords in purpose_keywords:
            if any(keyword in normalized for keyword in keywords):
                context.purpose = purpose
                break

    preference_keywords = {
        "nong": ["nong", "am bung", "am"],
        "mat": ["mat", "lanh", "giai nhiet"],
        "cay": ["cay", "sa te"],
        "it dau mo": ["it dau", "healthy", "lanh manh"],
        "an nhanh": ["nhanh", "mang di", "take away"],
        "yen tinh": ["yen tinh", "lam viec", "noi chuyen"],
        "mon la": ["mon la", "khac la", "khong phai do viet"],
    }
    for preference, keywords in preference_keywords.items():
        if any(keyword in normalized for keyword in keywords):
            _append_unique(context.preferences, preference)

    allergy_match = re.search(r"(?:di ung|khong an duoc|tranh)\s+([^,.!?]+)", normalized)
    if allergy_match:
        for allergy in re.split(r"\s*(?:,|/| va | voi )\s*", allergy_match.group(1)):
            _append_unique(context.allergies, allergy.strip())

    return last_user_msg


def _infer_intent_from_text(text: str) -> str | None:
    normalized = _normalize_text(text)
    cleaned = re.sub(r'[^\w\s]', '', normalized).strip()

    # ── Check greeting/xã giao trước ──
    greeting_exact = [
        "chao", "chao ban", "hello", "hi", "xin chao", "chao ad",
        "chao tro ly", "chao em", "tam biet", "cam on", "thank",
        "thanks", "bye", "goodbye", "hey",
    ]
    if cleaned in greeting_exact:
        return "greeting"
    if len(cleaned.split()) <= 4 and any(g in cleaned for g in ["chao", "hello", "hi ", "hey ", "cam on", "tam biet"]):
        return "greeting"

    # ── Check xem có liên quan ẩm thực không ──
    restaurant_terms = [
        "quan an", "nha hang", "gan toi", "gan day", "dia diem", "cho nao",
        "tim quan", "dat ban", "review", "danh gia",
    ]
    # Chỉ giữ các term rõ ràng về ý định ăn uống — bỏ "nhe", "nong", "mat" (quá chung)
    food_terms = [
        "an gi", "mon an", "do an", "goi y mon", "muon an", "an vat",
        "bua sang", "bua trua", "bua toi", "bua nhe",
        "mon ngon", "mon nong", "mon mat", "mon cay", "mon lanh",
        "an sang", "an trua", "an toi",
        "pho", "bun", "com", "banh mi", "chao", "lau", "che",
        "healthy", "khong cay", "it dau",
        "ngan sach", "budget", "duoi.*k",
        "trend", "hot", "xu huong", "thinh hanh",
    ]

    wants_restaurant = any(term in normalized for term in restaurant_terms)
    wants_food = any(
        re.search(rf"(?:^|\s){term}(?:\s|$)", normalized) if ".*" not in term
        else re.search(term, normalized)
        for term in food_terms
    )

    if wants_food and wants_restaurant:
        return "food_and_restaurant"
    if wants_food:
        return "food_only"
    if wants_restaurant:
        return "restaurant_only"

    # Nếu không match gì → trả "general" để xử lý bằng LLM thuần
    return "general"


def _fallback_foods(context: UserContext, user_query: str) -> list[dict]:
    normalized = _normalize_text(user_query)
    budget = context.budget or 100000
    wants_light = any(term in normalized for term in ["nhe", "de tieu", "healthy", "it dau"])
    wants_hot = any(term in normalized for term in ["nong", "am", "am bung", "mua", "lanh"])
    wants_cool = any(term in normalized for term in ["mat", "lanh", "giai nhiet"])

    candidates = [
        {
            "name": "Cháo gà hành gừng",
            "category": "Cháo",
            "description": "Món nóng, mềm, dễ tiêu, hợp khi muốn ăn nhẹ.",
            "estimated_price": 45000,
            "reason": "Ấm bụng, không quá nặng và phù hợp phần lớn ngân sách phổ thông.",
            "tags": ["nhẹ", "nóng", "dễ tiêu"],
        },
        {
            "name": "Bún riêu cua",
            "category": "Bún",
            "description": "Nước dùng thanh, khẩu phần vừa phải, dễ ăn.",
            "estimated_price": 55000,
            "reason": "Vừa có nước dùng nóng vừa không quá ngấy.",
            "tags": ["nhẹ", "nóng", "thanh"],
        },
        {
            "name": "Salad gà trái cây",
            "category": "Salad",
            "description": "Tươi mát, nhiều protein, ít dầu mỡ.",
            "estimated_price": 70000,
            "reason": "Hợp khi muốn ăn nhẹ, lành mạnh và không quá nặng bụng.",
            "tags": ["nhẹ", "healthy", "mát"],
        },
        {
            "name": "Gỏi cuốn tôm thịt",
            "category": "Cuốn",
            "description": "Rau tươi, bún, tôm thịt cuốn gọn, ăn nhẹ nhưng vẫn đủ chất.",
            "estimated_price": 40000,
            "reason": "Ít dầu mỡ, tiện ăn nhanh và hợp khẩu vị nhẹ nhàng.",
            "tags": ["nhẹ", "ít dầu mỡ", "tươi"],
        },
    ]

    filtered = [food for food in candidates if food["estimated_price"] <= budget]
    if wants_hot:
        hot_foods = [food for food in filtered if "nóng" in food["tags"]]
        if hot_foods:
            filtered = hot_foods
    elif wants_cool:
        cool_foods = [food for food in filtered if "mát" in food["tags"] or "tươi" in food["tags"]]
        if cool_foods:
            filtered = cool_foods
    elif wants_light:
        light_foods = [food for food in filtered if "nhẹ" in food["tags"]]
        if light_foods:
            filtered = light_foods

    return (filtered or candidates)[:3]


async def _stream_text(stream_callback: StreamCallback, text: str) -> None:
    cleaned = _strip_tool_artifacts(text)
    for word in cleaned.split(" "):
        await stream_callback("text", {"delta": word + " "})


def _build_local_final_text(food_names: list[str], intent: str) -> str:
    if food_names:
        names = ", ".join(food_names)
        text = f"Mình gợi ý bạn thử {names}. Các món này hợp với ngữ cảnh bạn nhập và khá dễ ăn."
    else:
        text = "Mình chưa đủ dữ liệu để chốt món thật chính xác, nhưng bạn có thể nói thêm ngân sách hoặc khẩu vị nhé."
    if intent in ("restaurant_only", "food_and_restaurant"):
        text += " Nếu muốn tìm quán gần bạn, hãy bật vị trí hoặc cho mình khu vực cụ thể."
    return text


async def run(
    messages: list[Message],
    context: UserContext,
    stream_callback: StreamCallback,
) -> None:
    """Điều phối pipeline. Hỗ trợ cả mock và real mode."""
    _enrich_context_from_messages(messages, context)

    # ── MOCK MODE ─────────────────────────────────────────────
    if MOCK_MODE:
        await _run_mock(messages, context, stream_callback)
        return

    # ── REAL MODE ─────────────────────────────────────────────
    await _run_real(messages, context, stream_callback)


async def _run_mock(
    messages: list[Message],
    context: UserContext,
    stream_callback: StreamCallback,
) -> None:
    """Chạy pipeline với mock data động — phản hồi đúng theo ngữ cảnh và câu hỏi của user."""
    import asyncio
    import re
    from services import scraper as scraper_service

    # 1. Thu thập thông tin từ tin nhắn cuối cùng của user
    last_user_msg = next((m.content for m in reversed(messages) if m.role == "user"), "").lower()

    # Kiểm tra xem tin nhắn có phải chỉ là lời chào/hỏi xã giao hay không
    greetings = ["chào", "chao", "hello", "hi", "xin chào", "xin chao", "chào bạn", "chao ban", "chào ad", "chao ad", "chào trợ lý", "chao tro ly", "chào em", "chao em", "tạm biệt", "tam biet", "cảm ơn", "cam on", "thank"]
    is_greeting = False
    cleaned_msg = re.sub(r'[^\w\s]', '', last_user_msg).strip()
    if cleaned_msg in greetings or any(cleaned_msg == g for g in greetings):
        is_greeting = True
    elif len(cleaned_msg.split()) <= 3 and any(g in cleaned_msg for g in ["chào", "chao", "hello", "hi"]):
        is_greeting = True

    if is_greeting:
        await stream_callback("thinking", {"status": "Đang phản hồi..."})
        await asyncio.sleep(0.3)
        final_text = "Xin chào bạn! Mình là trợ lý AI chuyên gợi ý món ăn và nhà hàng tại Việt Nam. Bạn đang cần tìm món ăn ngon phù hợp với thời tiết, tìm quán ăn gần đây, hay muốn biết các món hot trend/review ẩm thực? Hãy cho mình biết nhé! 😊"
        words = final_text.split(" ")
        for i, word in enumerate(words):
            chunk = word + (" " if i < len(words) - 1 else "")
            await stream_callback("text", {"delta": chunk})
            await asyncio.sleep(0.02)
        await stream_callback("done", {
            "follow_up_suggestions": [
                "Gợi ý món ăn hôm nay",
                "Tìm quán ăn gần đây",
                "Món gì đang hot trend vậy?"
            ]
        })
        return

    await stream_callback("thinking", {"status": "Đang phân tích yêu cầu của bạn..."})
    await asyncio.sleep(0.3)
    
    # Rút trích ngân sách từ text
    budget_limit = context.budget or 999999
    budget_match = re.search(r"dưới\s*(\d+)\s*k", last_user_msg)
    if budget_match:
        budget_limit = int(budget_match.group(1)) * 1000
    else:
        budget_match_raw = re.search(r"dưới\s*(\d+)\s*(\d{3})", last_user_msg)
        if budget_match_raw:
            budget_limit = int(budget_match_raw.group(1)) * 1000 + int(budget_match_raw.group(2))
        else:
            budget_match_num = re.search(r"dưới\s*(\d+)\s*(?:nghìn|ngàn|đ|vnd)", last_user_msg)
            if budget_match_num:
                num = int(budget_match_num.group(1))
                if num < 1000:
                    budget_limit = num * 1000
                else:
                    budget_limit = num

    # Kiểm tra yêu cầu hot trend
    is_trend_request = any(k in last_user_msg for k in ["trend", "hot", "xu hướng", "thịnh hành", "săn đón"])
    
    # Kiểm tra yêu cầu review
    is_review_request = any(k in last_user_msg for k in ["review", "đánh giá", "nhận xét"])

    # ─────────────────────────────────────────────
    # FLOW 1: Cào món ăn xu hướng (crawl_trending_foods)
    # ─────────────────────────────────────────────
    if is_trend_request:
        await stream_callback("thinking", {"status": "Đang cào món ăn hot trend từ internet (crawl_trending_foods)..."})
        await asyncio.sleep(0.8)
        
        # Gọi tool thật/mock scraper
        scrape_res = await scraper_service.crawl_trending_foods(last_user_msg)
        scrape_results = scrape_res.get("results", [])

        # Trích xuất từ khóa sạch
        query_clean = last_user_msg.replace("hot trend", "").replace("trend", "").replace("hot", "").replace("xu hướng", "").replace("thịnh hành", "").replace("săn đón", "").replace("món gì", "").replace("món", "").replace("đang", "").strip()
        if not query_clean:
            query_clean = "Món Ngon"

        selected_foods = []
        for idx, result_text in enumerate(scrape_results):
            words = result_text.split()
            food_name = ""
            for kw in ["cà phê muối", "trà sữa", "trà chanh giã tay", "bánh đồng xu", "gỏi cuốn", "phở bò", "bún chả", "lẩu", "cơm tấm", "bún riêu", "nem chua", "ốc nóng", "bánh mì", "kem", "chè"]:
                if kw in result_text.lower():
                    food_name = kw.title()
                    break
            
            if not food_name:
                food_name = " ".join(words[:3]).strip(".,-– ").title()
            
            if len(food_name) < 3:
                food_name = f"Trend {query_clean}".title()

            selected_foods.append({
                "name": food_name,
                "category": "Hot Trend",
                "description": result_text,
                "estimated_price": 30000 + idx * 5000,
                "reason": f"Dữ liệu cào thực tế từ Google: '{result_text[:80]}...'",
                "tags": ["hot trend", "cào mạng"]
            })
        
        await stream_callback("food_results", {"foods": selected_foods})
        await asyncio.sleep(0.2)

        final_text = (
            "🔥 **Danh sách món ăn Hot Trend & Xu hướng cào được mới nhất:**\n\n"
        )
        for f in selected_foods:
            final_text += f"🌟 **{f['name']}** (~{f['estimated_price']//1000}k) - {f['description']}\n\n"
            
        final_text += "\nBạn có muốn tìm quán bán các món trend này không? Hãy cho mình biết vị trí nhé! 📍"

        words = final_text.split(" ")
        for i, word in enumerate(words):
            chunk = word + (" " if i < len(words) - 1 else "")
            await stream_callback("text", {"delta": chunk})
            await asyncio.sleep(0.02)

        await stream_callback("done", {
            "follow_up_suggestions": [
                "Quán trà chanh gần nhất?",
                "Có món trend nào dưới 30k không?",
                "Tìm review về các món này",
            ]
        })
        return

    # ─────────────────────────────────────────────
    # FLOW 2: Cào đánh giá/review quán (crawl_restaurant_reviews)
    # ─────────────────────────────────────────────
    if is_review_request:
        # Tìm kiếm tên quán ăn
        rest_name = "Quán ăn"
        for word in ["phở bò lý quốc sư", "cơm tấm ba ghiền", "pizza 4ps", "phở thìn"]:
            if word in last_user_msg:
                rest_name = word.title()
                break
        if rest_name == "Quán ăn":
            match = re.search(r"(?:review|đánh giá|nhận xét)\s+(?:quán|nhà hàng)?\s*([^?📍\n]+)", last_user_msg)
            if match:
                rest_name = match.group(1).strip().title()

        await stream_callback("thinking", {"status": f"Đang cào review cho {rest_name} từ các blog ẩm thực (crawl_restaurant_reviews)..."})
        await asyncio.sleep(0.8)

        scrape_res = await scraper_service.crawl_restaurant_reviews(rest_name)
        reviews = scrape_res.get("reviews", [])

        final_text = (
            f"📝 **Kết quả cào đánh giá và review cho '{rest_name}':**\n\n"
        )
        for idx, rev in enumerate(reviews, 1):
            final_text += f"{idx}. *\"{rev}\"*\n"
            
        final_text += f"\nNhìn chung, **{rest_name}** nhận được phản hồi khá tích cực từ cộng đồng. Bạn có muốn mình tìm thêm đường đi hay thông tin chi tiết khác không? 🗺️"

        words = final_text.split(" ")
        for i, word in enumerate(words):
            chunk = word + (" " if i < len(words) - 1 else "")
            await stream_callback("text", {"delta": chunk})
            await asyncio.sleep(0.02)

        await stream_callback("done", {
            "follow_up_suggestions": [
                f"Tìm đường đến {rest_name}",
                "Gợi ý quán tương tự gần đây",
                "Xem thực đơn chi tiết",
            ]
        })
        return

    # ─────────────────────────────────────────────
    # FLOW 3: Gợi ý món ăn thông thường — Cào dữ liệu thật
    # ─────────────────────────────────────────────
    from tools.food_search.tool import handle as handle_food_search

    # Xác định thời tiết từ ngữ cảnh
    weather = "normal"
    if any(w in last_user_msg for w in ["nóng", "ấm", "mùa hè"]):
        weather = "hot"
    elif any(w in last_user_msg for w in ["lạnh", "mát", "mùa đông"]):
        weather = "cold"
    elif any(w in last_user_msg for w in ["mưa"]):
        weather = "rainy"

    # Xác định meal_time
    meal_time = "lunch"
    if any(w in last_user_msg for w in ["sáng", "breakfast"]):
        meal_time = "breakfast"
    elif any(w in last_user_msg for w in ["tối", "dinner"]):
        meal_time = "dinner"
    elif any(w in last_user_msg for w in ["vặt", "snack", "nhẹ"]):
        meal_time = "snack"

    # Trích xuất preferences từ tin nhắn
    prefs = []
    for kw_pair in [("cay", "cay"), ("ngọt", "ngọt"), ("healthy", "healthy"), ("giòn", "giòn")]:
        if kw_pair[0] in last_user_msg:
            prefs.append(kw_pair[1])

    # Gọi tool scraping thật
    await stream_callback("thinking", {"status": "Đang cào dữ liệu món ăn từ Google..."})
    food_result = await handle_food_search({
        "meal_time": meal_time,
        "budget": budget_limit if budget_limit < 999999 else 80000,
        "weather": weather,
        "preferences": prefs,
        "allergies": [],
    })

    selected_foods = food_result.get("foods", [])

    # Nếu scraping không ra kết quả, thông báo rõ
    if not selected_foods:
        await stream_callback("thinking", {"status": "Không cào được dữ liệu, đang thử lại..."})
        # Thử lại với query đơn giản
        food_result_retry = await handle_food_search({
            "meal_time": meal_time,
            "budget": 100000,
            "weather": "normal",
            "preferences": [],
            "allergies": [],
        })
        selected_foods = food_result_retry.get("foods", [])

    food_names = [f["name"] for f in selected_foods]

    await stream_callback("thinking", {"status": "Đang gợi ý món ăn phù hợp..."})
    await asyncio.sleep(0.4)

    # Gửi kết quả món ăn — chỉ gửi nếu có kết quả thật
    if selected_foods:
        await stream_callback("food_results", {"foods": selected_foods})
        await asyncio.sleep(0.2)

    # Lọc nhà hàng tương ứng
    if context.location and food_names:
        await stream_callback("thinking", {"status": "Đang tìm quán ăn gần bạn..."})
        await asyncio.sleep(0.4)

        from services.places import MOCK_RESTAURANTS
        matched_restaurants = []

        for rest in MOCK_RESTAURANTS:
            dishes = [d.lower() for d in rest.get("featured_dishes", [])]
            has_match = False
            for f in food_names:
                f_low = f.lower()
                if any(f_low in d for d in dishes) or f_low in rest["name"].lower():
                    has_match = True
                    break
            if has_match:
                matched_restaurants.append(rest)
        
        if not matched_restaurants:
            matched_restaurants = list(MOCK_RESTAURANTS)[:3]
            
        await stream_callback("restaurant_results", {"restaurants": matched_restaurants[:3]})
        await asyncio.sleep(0.2)

    await stream_callback("thinking", {"status": "Đang soạn gợi ý cho bạn..."})
    await asyncio.sleep(0.2)

    # Tạo prompt tổng hợp kết quả động
    if selected_foods:
        final_text = (
            f"Dựa trên dữ liệu cào từ Google, mình gợi ý cho bạn các món sau: 😊\n\n"
        )
        for f in selected_foods:
            tag_icon = "🍜" if "Bún" in f["name"] or "Phở" in f["name"] else "🍲" if "Cháo" in f["name"] or "Lẩu" in f["name"] else "🥗" if "Salad" in f["name"] else "🍞" if "Bánh mì" in f["name"] else "🍚" if "Cơm" in f["name"] else "🍧"
            final_text += f"{tag_icon} **{f['name']}** (~{f['estimated_price']//1000}k) — {f['description']}\n"
            
        final_text += "\nBạn có muốn mình tìm quán gần đây có bán các món này không? 📍"
    else:
        final_text = (
            "Xin lỗi, mình không cào được dữ liệu món ăn từ internet lúc này. 😔\n"
            "Bạn có thể thử hỏi cụ thể hơn (ví dụ: 'gợi ý phở ngon', 'bún chả Hà Nội') để mình tìm chính xác hơn nhé!"
        )

    # Stream text từng từ
    words = final_text.split(" ")
    for i, word in enumerate(words):
        chunk = word + (" " if i < len(words) - 1 else "")
        await stream_callback("text", {"delta": chunk})
        await asyncio.sleep(0.02)

    await stream_callback("done", {
        "follow_up_suggestions": [
            "Tôi muốn đổi sang món khác",
            "Quán nào gần nhất?",
            "Món gì đang hot trend?",
        ]
    })


async def _run_real(
    messages: list[Message],
    context: UserContext,
    stream_callback: StreamCallback,
) -> None:
    """Chạy pipeline thật với Gemini API."""
    last_user_msg = next((m.content for m in reversed(messages) if m.role == "user"), "")

    # Kiểm tra xem tin nhắn có phải chỉ là lời chào/hỏi xã giao hay không
    greetings = [
        "chào", "chao", "hello", "hi", "xin chào", "xin chao",
        "chào bạn", "chao ban", "chào ad", "chao ad",
        "chào trợ lý", "chao tro ly", "chào em", "chao em",
        "tạm biệt", "tam biet", "cảm ơn", "cam on", "thank", "thanks",
        "hey", "hi bạn", "hi ban", "hello bạn", "hello ban",
        "chào nhé", "chao nhe", "bye", "goodbye",
    ]
    is_greeting = False
    cleaned_msg = re.sub(r'[^\w\s]', '', last_user_msg.lower()).strip()
    # Check exact match
    if cleaned_msg in greetings:
        is_greeting = True
    # Check nếu tin nhắn ngắn (<=4 từ) và chứa từ chào
    elif len(cleaned_msg.split()) <= 4 and any(
        g in cleaned_msg for g in [
            "chào", "chao", "hello", "hi", "hey",
            "cảm ơn", "cam on", "tạm biệt", "tam biet",
            "thank", "bye",
        ]
    ):
        is_greeting = True

    if is_greeting:
        await stream_callback("thinking", {"status": "Đang phản hồi..."})
        await asyncio.sleep(0.3)
        final_text = "Xin chào bạn! Mình là trợ lý AI chuyên gợi ý món ăn và nhà hàng tại Việt Nam. Bạn đang cần tìm món ăn ngon phù hợp với thời tiết, tìm quán ăn gần đây, hay muốn biết các món hot trend/review ẩm thực? Hãy cho mình biết nhé! 😊"
        words = final_text.split(" ")
        for i, word in enumerate(words):
            chunk = word + (" " if i < len(words) - 1 else "")
            await stream_callback("text", {"delta": chunk})
            await asyncio.sleep(0.02)
        await stream_callback("done", {
            "follow_up_suggestions": [
                "Gợi ý món ăn hôm nay",
                "Tìm quán ăn gần đây",
                "Món gì đang hot trend vậy?"
            ]
        })
        return

    system = build_system_prompt(context)
    msg_dicts = [{"role": m.role, "content": m.content} for m in messages]
    inferred_intent = _infer_intent_from_text(last_user_msg)

    # ── Bước 1: Detect intent ──────────────────────────────────
    await stream_callback("thinking", {"status": "Đang phân tích yêu cầu của bạn..."})

    intent = inferred_intent or "food_and_restaurant"
    food_names: list[str] = []

    # ── Greeting / General intent → LLM thuần, KHÔNG gọi tool ──
    if intent in ("greeting", "general"):
        await stream_callback("thinking", {"status": "Đang phản hồi..."})
        try:
            llm_response = await asyncio.wait_for(
                llm.call(
                    system=system,
                    messages=msg_dicts,
                    stream=True,
                ),
                timeout=15,
            )
            if hasattr(llm_response, "__aiter__"):
                await _stream_llm_text(stream_callback, llm_response)
            else:
                await _stream_llm_text(stream_callback, llm_response)
        except Exception as e:
            print(f"[ERROR] LLM general response failed: {e}", file=sys.stderr)
            fallback_text = (
                "Xin chào! Mình là trợ lý AI chuyên về ẩm thực và nhà hàng Việt Nam. "
                "Bạn cần mình giúp gì về món ăn hoặc quán ăn không? 😊"
            )
            await _stream_text(stream_callback, fallback_text)

        follow_ups = [
            "Gợi ý món ăn hôm nay",
            "Tìm quán ăn gần đây",
            "Món gì đang hot trend vậy?",
        ]
        await stream_callback("done", {"follow_up_suggestions": follow_ups})
        return

    if inferred_intent and intent not in ("greeting", "general"):
        await stream_callback("thinking", {
            "status": f"Hiểu rồi! Đang tìm {'món ăn' if 'food' in intent else 'quán ăn'}..."
        })
    else:
        try:
            intent_response = await asyncio.wait_for(
                llm.call(
                    system=system,
                    messages=msg_dicts,
                    tools=to_gemini_tools(["detect_intent", "run_food_agent", "run_restaurant_agent"]),
                ),
                timeout=12,
            )
        except Exception as e:
            await stream_callback("thinking", {
                "status": f"AI phản hồi chậm, mình sẽ gợi ý nhanh theo ngữ cảnh hiện có..."
            })
            intent_response = None

        if intent_response and intent_response.candidates and intent_response.candidates[0].content and intent_response.candidates[0].content.parts:
            for part in intent_response.candidates[0].content.parts:
                if part.function_call and part.function_call.name == "detect_intent":
                    args = dict(part.function_call.args) if part.function_call.args else {}
                    intent = args.get("intent", "food_and_restaurant")
                    await stream_callback("thinking", {
                        "status": f"Hiểu rồi! Đang tìm {'món ăn' if 'food' in intent else 'quán ăn'}..."
                    })
                    break

    # ── Bước 2: Food agent ─────────────────────────────────────
    if intent in ("food_only", "food_and_restaurant", "food_info"):
        await stream_callback("thinking", {"status": "Đang gợi ý món ăn phù hợp..."})
        simple_food_intent = any(k in _normalize_text(last_user_msg) for k in [
            "cay", "spicy", "món cay", "mon cay", "lẩu cay", "mì cay", "bun bo hue",
            "gan toi", "gần tôi", "gan day", "near me", "dưới", "duoi", "trend", "hot"
        ])
        try:
            if simple_food_intent:
                food_result = await asyncio.wait_for(food_agent.search_direct(context, last_user_msg), timeout=8)
            else:
                food_result = await asyncio.wait_for(food_agent.run(context, last_user_msg), timeout=12)
        except Exception:
            food_result = {"foods": [], "food_names": []}

        if food_result.get("ask"):
            await stream_callback("ask_context", {
                "field": food_result["field"],
                "message": food_result["message"],
            })
            return

        foods = food_result.get("foods", [])
        food_names = food_result.get("food_names", [])
        if not foods:
            fallback = await food_agent.search_direct(context, last_user_msg)
            foods = fallback.get("foods", [])
            food_names = fallback.get("food_names", [])
        if foods:
            await stream_callback("food_results", {"foods": foods})
        else:
            await stream_callback("thinking", {
                "status": "Không tìm thấy dữ liệu món ăn phù hợp, đang thử cách khác..."
            })

    # ── Bước 3: Restaurant agent ───────────────────────────────
    if intent in ("restaurant_only", "food_and_restaurant"):
        if context.location:
            await stream_callback("thinking", {"status": "Đang tìm quán ăn gần bạn..."})
            restaurant_result = await restaurant_agent.run(context, food_names, last_user_msg)

            if restaurant_result.get("ask"):
                await stream_callback("ask_context", {
                    "field": restaurant_result["field"],
                    "message": restaurant_result["message"],
                })
                return

            restaurants = restaurant_result.get("restaurants", [])
            if restaurants:
                await stream_callback("restaurant_results", {"restaurants": restaurants})
        else:
            await stream_callback("ask_context", {
                "field": "location",
                "message": "Bạn có thể cho tôi biết bạn đang ở đâu không? Tôi cần vị trí để tìm quán ăn gần bạn nhé! 📍",
            })
            return

    # ── Bước 4: Final stream ───────────────────────────────────
    await stream_callback("thinking", {"status": "Đang soạn gợi ý cho bạn..."})

    final_prompt = _build_final_prompt(messages, food_names, intent)

    if inferred_intent == "food_only" and food_names:
        await _stream_text(stream_callback, _build_local_final_text(food_names, intent))
        follow_ups = _generate_follow_ups(intent, food_names)
        await stream_callback("done", {"follow_up_suggestions": follow_ups})
        return

    try:
        stream = await asyncio.wait_for(
            llm.call(
                system=system,
                messages=[{"role": "user", "content": final_prompt}],
                stream=True,
            ),
            timeout=15,
        )
        if hasattr(stream, "__aiter__"):
            await _stream_llm_text(stream_callback, stream)
        else:
            await _stream_llm_text(stream_callback, stream)
    except Exception as e:
        print(f"[ERROR] Final stream failed: {e}", file=sys.stderr)
        try:
            resp = await asyncio.wait_for(
                llm.call(
                    system=system,
                    messages=[{"role": "user", "content": final_prompt}],
                ),
                timeout=10,
            )
            if resp.text:
                await _stream_text(stream_callback, resp.text)
        except Exception as e2:
            await _stream_text(stream_callback, _build_local_final_text(food_names, intent))

    follow_ups = _generate_follow_ups(intent, food_names)
    await stream_callback("done", {"follow_up_suggestions": follow_ups})


def _build_final_prompt(messages: list[Message], food_names: list[str], intent: str) -> str:
    last_user_msg = next(
        (m.content for m in reversed(messages) if m.role == "user"), ""
    )
    parts = [f"Người dùng hỏi: {last_user_msg}"]
    if food_names:
        parts.append(f"Món ăn đề xuất: {', '.join(food_names)}")
    parts.append(
        "Hệ thống đã gọi tool và có kết quả ở trên (nếu có). "
        "Hãy tổng hợp và trả lời thân thiện bằng tiếng Việt. "
        "Giải thích ngắn gọn lý do gợi ý. "
        "TUYỆT ĐỐI KHÔNG in code, thẻ <tool_code>, hay mô phỏng gọi tool. "
        "Thêm disclaimer nếu có liên quan đến sức khỏe/dị ứng."
    )
    return "\n".join(parts)


def _generate_follow_ups(intent: str, food_names: list[str]) -> list[str]:
    suggestions = []
    if food_names:
        suggestions.append("Tôi muốn đổi sang món khác")
        suggestions.append(f"Quán nào có {food_names[0]} giá tốt nhất?")
    else:
        suggestions.append("Gợi ý món ăn nhẹ dưới 50k")
    suggestions.append("Tôi muốn ăn gì đó khác hơn")
    if intent in ("restaurant_only", "food_and_restaurant"):
        suggestions.append("Tìm quán có chỗ ngồi yên tĩnh làm việc")
    return suggestions[:3]
