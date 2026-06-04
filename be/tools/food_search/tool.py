"""
Food Search Tool — cào dữ liệu món ăn thật từ internet.
Sử dụng DuckDuckGo HTML (scraper-friendly) thay vì Google.
"""
import sys
import re
import httpx
from bs4 import BeautifulSoup

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


async def handle(tool_input: dict) -> dict:
    """
    Cào dữ liệu món ăn thực tế từ internet dựa trên tiêu chí người dùng.
    KHÔNG dùng LLM generate — chỉ trả kết quả từ dữ liệu cào.
    """
    meal_time = str(tool_input.get("meal_time", "lunch")).lower()
    if meal_time not in ["breakfast", "lunch", "dinner", "snack"]:
        meal_time = "lunch"

    try:
        budget = int(tool_input.get("budget", 80000))
        if budget <= 0:
            budget = 80000
    except (ValueError, TypeError):
        budget = 80000

    prefs_raw = tool_input.get("preferences", [])
    if not isinstance(prefs_raw, list):
        prefs_raw = []
    preferences = [str(p).strip() for p in prefs_raw if p]

    allergies_raw = tool_input.get("allergies", [])
    if not isinstance(allergies_raw, list):
        allergies_raw = []
    allergies = [str(a).strip() for a in allergies_raw if a]

    weather = str(tool_input.get("weather", "normal")).lower()
    if weather not in ["hot", "cold", "rainy", "normal"]:
        weather = "normal"

    # Build search query từ tiêu chí
    search_query = _build_search_query(meal_time, budget, weather, preferences)

    # Cào dữ liệu thật
    foods = await _scrape_foods(search_query, budget, allergies)

    if foods:
        return {"foods": foods, "source": "web_scrape", "query": search_query}

    # Thử lại với query đơn giản hơn
    simple_query = _build_simple_query(meal_time, weather)
    foods = await _scrape_foods(simple_query, budget, allergies)

    if foods:
        return {"foods": foods, "source": "web_scrape_simple", "query": simple_query}

    return {
        "foods": [],
        "source": "scrape_failed",
        "error": "Không thể cào dữ liệu món ăn từ internet. Vui lòng thử lại với từ khóa khác.",
    }


def _build_search_query(meal_time: str, budget: int, weather: str, preferences: list[str]) -> str:
    """Xây dựng query tìm kiếm từ tiêu chí."""
    weather_vi = {
        "hot": "trời nóng", "cold": "trời lạnh",
        "rainy": "trời mưa", "normal": "",
    }.get(weather, "")

    meal_vi = {
        "breakfast": "bữa sáng", "lunch": "bữa trưa",
        "dinner": "bữa tối", "snack": "ăn vặt",
    }.get(meal_time, "")

    parts = ["gợi ý món ăn ngon Việt Nam"]
    if meal_vi:
        parts.append(meal_vi)
    if weather_vi:
        parts.append(weather_vi)
    if budget and budget < 200000:
        parts.append(f"dưới {budget // 1000}k")
    if preferences:
        parts.extend(preferences[:2])

    return " ".join(parts)


def _build_simple_query(meal_time: str, weather: str) -> str:
    """Query đơn giản hơn để fallback."""
    meal_vi = {
        "breakfast": "sáng", "lunch": "trưa",
        "dinner": "tối", "snack": "vặt",
    }.get(meal_time, "trưa")

    weather_vi = {
        "hot": "mùa hè", "cold": "mùa đông",
        "rainy": "mưa", "normal": "",
    }.get(weather, "")

    q = f"top món ăn {meal_vi} ngon nhất Việt Nam"
    if weather_vi:
        q += f" {weather_vi}"
    return q


async def _scrape_foods(query: str, budget: int, allergies: list[str]) -> list[dict]:
    """Cào search results và trích xuất thông tin món ăn."""
    snippets = await _search_duckduckgo(query)

    if not snippets:
        # Fallback: thử Bing
        snippets = await _search_bing(query)

    if not snippets:
        return []

    foods = _parse_foods_from_snippets(snippets, budget, allergies)
    return foods


async def _search_duckduckgo(query: str) -> list[str]:
    """Cào DuckDuckGo HTML search — thân thiện với scraper."""
    encoded = query.replace(" ", "+")
    url = f"https://html.duckduckgo.com/html/?q={encoded}"

    try:
        async with httpx.AsyncClient(timeout=12, follow_redirects=True) as client:
            resp = await client.get(url, headers=HEADERS)
            if resp.status_code != 200:
                print(f"[WARNING] DuckDuckGo returned {resp.status_code}", file=sys.stderr)
                return []

            soup = BeautifulSoup(resp.text, "html.parser")
            snippets = []
            seen = set()

            # DuckDuckGo HTML selectors
            for el in soup.find_all("a", {"class": "result__snippet"}):
                text = el.get_text(separator=" ").strip()
                if text and len(text) > 15 and text not in seen:
                    seen.add(text)
                    snippets.append(text)

            # Also grab result titles
            for el in soup.find_all("a", {"class": "result__a"}):
                text = el.get_text().strip()
                if text and len(text) > 5 and text not in seen:
                    seen.add(text)
                    snippets.append(text)

            # Alternative selectors
            if not snippets:
                for el in soup.find_all("td", {"class": "result-snippet"}):
                    text = el.get_text(separator=" ").strip()
                    if text and len(text) > 15 and text not in seen:
                        seen.add(text)
                        snippets.append(text)

            return snippets[:12]

    except Exception as e:
        print(f"[WARNING] DuckDuckGo search failed: {e}", file=sys.stderr)
        return []


async def _search_bing(query: str) -> list[str]:
    """Fallback: cào Bing search."""
    encoded = query.replace(" ", "+")
    url = f"https://www.bing.com/search?q={encoded}&setlang=vi"

    try:
        async with httpx.AsyncClient(timeout=12, follow_redirects=True) as client:
            resp = await client.get(url, headers=HEADERS)
            if resp.status_code != 200:
                return []

            soup = BeautifulSoup(resp.text, "html.parser")
            snippets = []
            seen = set()

            # Bing snippet selectors
            for el in soup.find_all("p", {"class": re.compile(r"b_lineclamp")}):
                text = el.get_text(separator=" ").strip()
                if text and len(text) > 20 and text not in seen:
                    seen.add(text)
                    snippets.append(text)

            for el in soup.find_all("li", {"class": "b_algo"}):
                text = el.get_text(separator=" ").strip()
                if text and len(text) > 30 and text not in seen:
                    seen.add(text)
                    snippets.append(text)

            # Bing captions
            for el in soup.find_all("div", {"class": "b_caption"}):
                text = el.get_text(separator=" ").strip()
                if text and len(text) > 20 and text not in seen:
                    seen.add(text)
                    snippets.append(text)

            return snippets[:12]

    except Exception as e:
        print(f"[WARNING] Bing search failed: {e}", file=sys.stderr)
        return []


def _parse_foods_from_snippets(
    snippets: list[str], budget: int, allergies: list[str]
) -> list[dict]:
    """Parse food names và thông tin từ search snippets."""
    foods: list[dict] = []
    seen_names: set[str] = set()

    # Danh sách món ăn Việt Nam phổ biến để match chính xác
    known_dishes = [
        "Phở bò", "Phở gà", "Bún bò Huế", "Bún chả", "Bún riêu cua",
        "Bún đậu mắm tôm", "Bún thịt nướng", "Bún cá", "Bún mắm",
        "Cơm tấm", "Cơm tấm sườn nướng", "Cơm gà", "Cơm gà xối mỡ",
        "Cơm rang dưa bò", "Cơm chiên", "Cơm cháy",
        "Bánh mì", "Bánh mì thịt", "Bánh xèo", "Bánh cuốn", "Bánh canh",
        "Bánh tráng trộn", "Bánh đa cua", "Bánh khọt",
        "Cháo gà", "Cháo sườn", "Cháo lòng",
        "Hủ tiếu", "Hủ tiếu Nam Vang", "Mì Quảng", "Cao lầu", "Mì xào",
        "Gỏi cuốn", "Gỏi đu đủ", "Nem rán", "Nem chua",
        "Lẩu thái", "Lẩu bò", "Lẩu gà", "Lẩu hải sản", "Lẩu nấm",
        "Chè thái", "Chè đậu", "Chè bưởi",
        "Xôi xéo", "Xôi gà", "Xôi lạc",
        "Cà phê muối", "Cà phê sữa đá", "Trà chanh", "Trà đá",
        "Ốc luộc", "Ốc nóng", "Sò huyết",
        "Thịt kho tàu", "Thịt nướng", "Gà nướng", "Gà rán",
        "Canh chua", "Canh bí đỏ", "Canh rau",
        "Salad", "Sinh tố", "Nước ép",
    ]

    # Bước 1: Match chính xác với known_dishes
    full_text = " ".join(snippets).lower()
    for dish in known_dishes:
        dish_lower = dish.lower()
        if dish_lower in full_text and dish_lower.replace(" ", "") not in seen_names:
            # Tìm snippet chứa dish này
            src_snippet = next((s for s in snippets if dish_lower in s.lower()), snippets[0] if snippets else "")

            # Skip nếu dị ứng
            if allergies and any(a.lower() in dish_lower for a in allergies):
                continue

            price = _estimate_price(src_snippet, dish)
            if price > budget * 1.2:
                continue

            seen_names.add(dish_lower.replace(" ", ""))
            foods.append({
                "name": dish,
                "category": _categorize(dish),
                "description": _extract_description(src_snippet, dish),
                "estimated_price": price,
                "reason": "Dữ liệu cào thực tế từ internet — phù hợp tiêu chí tìm kiếm.",
                "tags": _extract_tags(src_snippet, dish),
            })

            if len(foods) >= 5:
                return foods

    # Bước 2: Regex extraction cho các món chưa match
    # Stop words để cắt tên món
    stop_re = r"(?:\s+(?:với|cho|của|thêm|được|rất|là|có|và|mà|từ|gia đình|đầy đủ|đa dạng|thơm ngon|cách làm|ngon miệng|dinh dưỡng))"

    food_prefixes = (
        r"(?:Phở|Bún|Bánh|Cơm|Cháo|Chè|Lẩu|Nem|Gỏi|Xôi|Mì|Hủ tiếu|Miến|"
        r"Ốc|Tôm|Cua|Gà|Bò|Vịt|Cá|Canh|Sườn|Thịt|"
        r"Trà|Cà phê|Sinh tố|Nước|Kem|Sữa chua)"
    )

    pattern = rf"({food_prefixes}(?:\s+[\wàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]+){{1,4}})"

    for snippet in snippets:
        matches = re.findall(pattern, snippet, re.IGNORECASE | re.UNICODE)
        for match in matches:
            name = match.strip()
            # Cắt tại stop words
            name = re.split(stop_re, name, maxsplit=1, flags=re.IGNORECASE)[0].strip()
            name = name.strip(".,;:!?-– \t\n")
            name = re.sub(r"\s+", " ", name).strip()

            if len(name) < 4 or len(name) > 40:
                continue

            lower_name = name.lower()

            # Skip non-food phrases
            skip_phrases = [
                "gia đình", "thêm ngon", "ngon miệng", "đầy đủ",
                "đa dạng", "dinh dưỡng", "cách làm", "thực đơn",
                "bài viết", "gợi ý", "ăn trưa đa", "khô đến",
            ]
            if any(sp in lower_name for sp in skip_phrases):
                continue

            # Skip nếu quá chung
            if len(name.split()) <= 1 and len(name) < 5:
                continue

            name_key = lower_name.replace(" ", "")
            if name_key in seen_names:
                continue
            if allergies and any(a.lower() in lower_name for a in allergies):
                continue

            seen_names.add(name_key)
            price = _estimate_price(snippet, name)
            if price > budget * 1.2:
                continue

            foods.append({
                "name": _title_case_vn(name),
                "category": _categorize(name),
                "description": _extract_description(snippet, name),
                "estimated_price": price,
                "reason": "Dữ liệu cào thực tế từ internet — phù hợp tiêu chí tìm kiếm.",
                "tags": _extract_tags(snippet, name),
            })

            if len(foods) >= 5:
                return foods

    return foods


def _title_case_vn(name: str) -> str:
    """Title case cho tiếng Việt."""
    words = name.split()
    if not words:
        return name
    return words[0].capitalize() + (" " + " ".join(words[1:]) if len(words) > 1 else "")


def _estimate_price(snippet: str, name: str) -> int:
    """Ước lượng giá từ snippet context."""
    price_patterns = [
        r"(\d{2,3})[.\s]*(?:000|k|nghìn|ngàn)\s*(?:VND|đồng|vnđ|đ)?",
        r"(?:giá|khoảng|từ|chỉ)\s*(\d{2,3})\s*[kK]",
        r"(\d{2,3})\s*-\s*\d{2,3}\s*[kK]",
    ]
    for pattern in price_patterns:
        match = re.search(pattern, snippet, re.IGNORECASE)
        if match:
            try:
                val = int(match.group(1))
                if 5 <= val <= 500:
                    return val * 1000
            except ValueError:
                pass

    lower_name = name.lower()
    if any(w in lower_name for w in ["chè", "kem", "xôi", "bánh tráng"]):
        return 20000
    if any(w in lower_name for w in ["bánh mì", "bánh cuốn", "gỏi cuốn"]):
        return 30000
    if any(w in lower_name for w in ["phở", "bún", "cháo", "hủ tiếu", "mì", "miến"]):
        return 50000
    if any(w in lower_name for w in ["cơm", "sườn"]):
        return 55000
    if any(w in lower_name for w in ["lẩu"]):
        return 80000
    if any(w in lower_name for w in ["cà phê", "trà", "sinh tố", "nước"]):
        return 30000
    return 45000


def _categorize(name: str) -> str:
    """Phân loại món ăn theo tên."""
    lower = name.lower()
    categories = {
        "Phở": ["phở"], "Bún": ["bún"], "Cơm": ["cơm"], "Cháo": ["cháo"],
        "Bánh": ["bánh"], "Lẩu": ["lẩu"],
        "Chè/Tráng miệng": ["chè", "kem", "sữa chua"],
        "Xôi": ["xôi"],
        "Đồ uống": ["cà phê", "trà", "sinh tố", "nước"],
        "Ăn vặt": ["nem", "gỏi", "ốc", "sò", "bánh tráng"],
        "Mì/Miến": ["mì", "miến", "hủ tiếu", "nui"],
        "Canh/Súp": ["canh", "súp"],
    }
    for cat, keywords in categories.items():
        if any(kw in lower for kw in keywords):
            return cat
    return "Món ăn"


def _extract_description(snippet: str, name: str) -> str:
    """Trích xuất mô tả ngắn từ snippet."""
    sentences = re.split(r"[.!?]", snippet)
    for s in sentences:
        s_clean = s.strip()
        if name.lower() in s_clean.lower() and 15 < len(s_clean) < 150:
            return s_clean

    valid_sentences = [s.strip() for s in sentences if 15 < len(s.strip()) < 150]
    if valid_sentences:
        return max(valid_sentences, key=len)

    return snippet[:100].strip()


def _extract_tags(snippet: str, name: str) -> list[str]:
    """Trích xuất tags từ snippet."""
    tags = []
    lower = (snippet + " " + name).lower()
    tag_map = {
        "nóng": ["nóng", "ấm", "hổi", "nướng"],
        "lạnh": ["lạnh", "mát", "đá", "giải nhiệt"],
        "cay": ["cay", "sa tế", "ớt"],
        "ngọt": ["ngọt", "đường"],
        "giòn": ["giòn", "chiên", "rán"],
        "healthy": ["healthy", "lành mạnh", "ít dầu", "rau"],
        "no bụng": ["no", "đầy đủ", "chắc bụng"],
        "ăn vặt": ["ăn vặt", "snack", "nhẹ"],
        "phổ biến": ["phổ biến", "nổi tiếng", "yêu thích"],
        "đặc sản": ["đặc sản", "truyền thống", "cổ truyền"],
    }
    for tag, keywords in tag_map.items():
        if any(kw in lower for kw in keywords):
            tags.append(tag)
    return tags[:3] if tags else ["gợi ý"]
