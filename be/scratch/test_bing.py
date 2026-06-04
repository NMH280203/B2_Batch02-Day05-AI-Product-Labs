import httpx
import re
from bs4 import BeautifulSoup

async def main():
    query = "món ăn trưa ngon Việt Nam"
    encoded = query.replace(" ", "+")
    url = f"https://www.bing.com/search?q={encoded}&setlang=vi"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8"
    }
    
    print("Testing Bing GET...")
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, headers=headers)
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                
                # In ra độ dài của HTML để check có nội dung không
                print(f"HTML length: {len(resp.text)}")
                
                # Tìm các thẻ p class b_lineclamp
                snippets = []
                for el in soup.find_all("p", {"class": re.compile(r"b_lineclamp")}):
                    snippets.append(el.get_text())
                
                print(f"Found b_lineclamp count: {len(snippets)}")
                for i, s in enumerate(snippets[:3]):
                    print(f"Snippet {i}: {s[:150]}")
                    
                # Nếu không có, thử tìm thẻ div class b_caption hoặc li class b_algo
                if not snippets:
                    captions = []
                    for el in soup.find_all("div", {"class": "b_caption"}):
                        captions.append(el.get_text())
                    print(f"Found b_caption count: {len(captions)}")
                    for i, s in enumerate(captions[:3]):
                        print(f"Caption {i}: {s[:150]}")
                    
                    algos = []
                    for el in soup.find_all("li", {"class": "b_algo"}):
                        algos.append(el.get_text())
                    print(f"Found b_algo count: {len(algos)}")
                    for i, s in enumerate(algos[:3]):
                        print(f"Algo {i}: {s[:150]}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
