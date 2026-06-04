import asyncio
import httpx

async def test_server(name, url):
    print(f"Testing {name} ({url})...")
    query = """
    [out:json];
    (
      node(around:1500,10.7769,106.7009)[amenity=restaurant];
    );
    out body 10;
    """
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate"
    }
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, data={"data": query}, headers=headers)
            print(f"[{name}] POST Status: {resp.status_code}")
            if resp.status_code == 200:
                print(f"[{name}] Success! elements count: {len(resp.json().get('elements', []))}")
                return True
    except Exception as e:
        print(f"[{name}] POST Failed: {e}")
        
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, params={"data": query}, headers=headers)
            print(f"[{name}] GET Status: {resp.status_code}")
            if resp.status_code == 200:
                print(f"[{name}] Success! elements count: {len(resp.json().get('elements', []))}")
                return True
    except Exception as e:
        print(f"[{name}] GET Failed: {e}")
        
    return False

async def main():
    servers = {
        "DE (Main)": "https://overpass-api.de/api/interpreter",
        "Kumi": "https://overpass.kumi.systems/api/interpreter",
        "French": "https://overpass.n.openstreetmap.fr/api/interpreter",
        "Swiss": "https://overpass.osm.ch/api/interpreter"
    }
    
    for name, url in servers.items():
        res = await test_server(name, url)
        if res:
            print(f"\n---> {name} is working!\n")

if __name__ == "__main__":
    asyncio.run(main())
