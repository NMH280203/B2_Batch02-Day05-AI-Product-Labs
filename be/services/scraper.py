"""
Scraper Service — cào dữ liệu thật từ DuckDuckGo/Bing Search.
Dùng cho crawl_trending_foods và crawl_restaurant_reviews.
KHÔNG trả mock data — trả thông báo lỗi rõ ràng khi thất bại.
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


async def _search_web(query: str, min_length: int = 20) -> list[str]:
    """Cào search results từ DuckDuckGo HTML (primary) hoặc Bing (fallback)."""
    snippets = await _search_duckduckgo(query, min_length)
    if snippets:
        return snippets

    snippets = await _search_bing(query, min_length)
    return snippets


async def _search_duckduckgo(query: str, min_length: int = 20) -> list[str]:
    """Cào DuckDuckGo HTML — thân thiện với scraper."""
    encoded = query.replace(" ", "+")
    url = f"https://html.duckduckgo.com/html/?q={encoded}"

    try:
        async with httpx.AsyncClient(timeout=12, follow_redirects=True) as client:
            resp = await client.get(url, headers=HEADERS)
            if resp.status_code != 200:
                return []

            soup = BeautifulSoup(resp.text, "html.parser")
            snippets = []
            seen = set()

            # Snippet results
            for el in soup.find_all("a", {"class": "result__snippet"}):
                text = el.get_text(separator=" ").strip()
                if text and len(text) > min_length and text not in seen:
                    seen.add(text)
                    snippets.append(text)

            # Result titles
            for el in soup.find_all("a", {"class": "result__a"}):
                text = el.get_text().strip()
                if text and len(text) > 5 and text not in seen:
                    seen.add(text)
                    snippets.append(text)

            # Alternative selectors
            if not snippets:
                for el in soup.find_all("td", {"class": "result-snippet"}):
                    text = el.get_text(separator=" ").strip()
                    if text and len(text) > min_length and text not in seen:
                        seen.add(text)
                        snippets.append(text)

            return snippets[:8]

    except Exception as e:
        print(f"[WARNING] DuckDuckGo search failed: {e}", file=sys.stderr)
        return []


async def _search_bing(query: str, min_length: int = 20) -> list[str]:
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

            for el in soup.find_all("p", {"class": re.compile(r"b_lineclamp")}):
                text = el.get_text(separator=" ").strip()
                if text and len(text) > min_length and text not in seen:
                    seen.add(text)
                    snippets.append(text)

            for el in soup.find_all("div", {"class": "b_caption"}):
                text = el.get_text(separator=" ").strip()
                if text and len(text) > min_length and text not in seen:
                    seen.add(text)
                    snippets.append(text)

            return snippets[:8]

    except Exception as e:
        print(f"[WARNING] Bing search failed: {e}", file=sys.stderr)
        return []


async def crawl_trending_foods(query: str) -> dict:
    """
    Cào thông tin món ăn đang hot/phổ biến dựa trên từ khóa.
    Chỉ trả dữ liệu thật — nếu không cào được thì trả rỗng + lỗi.
    """
    search_query = f"món ăn hot trend {query} mới nhất Việt Nam"
    snippets = await _search_web(search_query, min_length=25)

    if snippets:
        return {
            "query": query,
            "source": "web_scrape",
            "results": snippets[:5],
        }

    # Thử query khác
    alt_query = f"xu hướng ẩm thực {query} đang thịnh hành"
    snippets = await _search_web(alt_query, min_length=25)

    if snippets:
        return {
            "query": query,
            "source": "web_scrape_alt",
            "results": snippets[:5],
        }

    return {
        "query": query,
        "source": "scrape_failed",
        "results": [],
        "error": f"Không thể cào dữ liệu trending cho '{query}'.",
    }


async def crawl_restaurant_reviews(restaurant_name: str) -> dict:
    """
    Cào các đánh giá/review của quán ăn trên mạng.
    Chỉ trả dữ liệu thật — nếu không cào được thì trả rỗng + lỗi.
    """
    search_query = f"review đánh giá quán {restaurant_name} có ngon không"
    snippets = await _search_web(search_query, min_length=30)

    if snippets:
        return {
            "restaurant": restaurant_name,
            "source": "web_scrape",
            "reviews": snippets[:5],
        }

    # Thử query khác
    alt_query = f"{restaurant_name} review khách hàng nhận xét"
    snippets = await _search_web(alt_query, min_length=30)

    if snippets:
        return {
            "restaurant": restaurant_name,
            "source": "web_scrape_alt",
            "reviews": snippets[:5],
        }

    return {
        "restaurant": restaurant_name,
        "source": "scrape_failed",
        "reviews": [],
        "error": f"Không thể cào review cho '{restaurant_name}'.",
    }
