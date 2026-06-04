import asyncio
import httpx

async def test():
    urls = [
        "https://lz4.overpass-api.de/api/interpreter",
        "https://z.overpass-api.de/api/interpreter",
        "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    ]
    
    query = '[out:json];node(around:1500,10.7769,106.7009)[amenity=restaurant];out body 5;'
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    
    for url in urls:
        print(f"Testing {url} ...")
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(url, data={"data": query}, headers=headers)
                print(f"POST Status: {resp.status_code}")
                if resp.status_code == 200:
                    print(f"Success! Elements found: {len(resp.json().get('elements', []))}")
        except Exception as e:
            print(f"Failed: {e}")
            
if __name__ == "__main__":
    asyncio.run(test())
