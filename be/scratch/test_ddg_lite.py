import httpx
from bs4 import BeautifulSoup

async def main():
    url = "https://lite.duckduckgo.com/lite/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    }
    data = {"q": "món ăn trưa ngon Việt Nam"}
    
    print("Testing DDG Lite POST...")
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, data=data, headers=headers)
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                # DuckDuckGo Lite selectors: 
                # Cấu trúc của Lite: các kết quả nằm trong bảng <table>
                # Mỗi kết quả có class="result-link" và snippet nằm dưới đó
                links = soup.find_all("a", {"class": "result-link"})
                print(f"Found links count: {len(links)}")
                for i, link in enumerate(links[:3]):
                    print(f"Link {i}: {link.get_text().strip()}")
                    # Snippet là thẻ td tiếp theo hoặc tr tiếp theo có class="result-snippet"
                    # Hãy tìm tr tiếp theo chứa class="result-snippet"
                    tr = link.find_parent("tr")
                    if tr:
                        next_tr = tr.find_next_sibling("tr")
                        if next_tr:
                            snippet_td = next_tr.find("td", {"class": "result-snippet"})
                            if snippet_td:
                                print(f"  Snippet: {snippet_td.get_text().strip()}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
