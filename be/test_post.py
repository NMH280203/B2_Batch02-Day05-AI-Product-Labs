import asyncio
import httpx

async def test():
    url = "https://overpass-api.de/api/interpreter"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    query = """
    [out:json];
    (
      node(around:1500,10.7769,106.7009)[amenity=restaurant];
    );
    out body;
    """
    
    print("Testing GET request...")
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, params={"data": query}, headers=headers)
            print(f"GET Status: {resp.status_code}")
            if resp.status_code == 200:
                print(f"GET returned elements count: {len(resp.json().get('elements', []))}")
    except Exception as e:
        print(f"GET failed: {e}")

    print("\nTesting POST request...")
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, data={"data": query}, headers=headers)
            print(f"POST Status: {resp.status_code}")
            if resp.status_code == 200:
                print(f"POST returned elements count: {len(resp.json().get('elements', []))}")
    except Exception as e:
        print(f"POST failed: {e}")

if __name__ == "__main__":
    asyncio.run(test())
