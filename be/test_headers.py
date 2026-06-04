import asyncio
import httpx

async def test():
    url = "https://overpass-api.de/api/interpreter"
    
    query = """
    [out:json];
    (
      node(around:1500,10.7769,106.7009)[amenity=restaurant];
    );
    out body;
    """
    
    # 1. Test requests with no extra headers (default httpx)
    print("1. Standard HTTPX request...")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, data={"data": query})
            print(f"Status: {resp.status_code}")
    except Exception as e:
        print(f"Failed: {e}")

    # 2. Test request with custom Accept
    print("\n2. Custom Accept: application/json ...")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url, 
                data={"data": query}, 
                headers={
                    "User-Agent": "Mozilla/5.0", 
                    "Accept": "application/json"
                }
            )
            print(f"Status: {resp.status_code}")
    except Exception as e:
        print(f"Failed: {e}")

    # 3. Test request with no Accept-Encoding
    print("\n3. Custom Accept-Encoding (empty/none) ...")
    try:
        async with httpx.AsyncClient() as client:
            # httpx default client sends default headers. We can disable them by setting headers to None or custom.
            resp = await client.post(
                url, 
                data={"data": query}, 
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                    "Accept": "*/*",
                    "Accept-Encoding": "identity" # identity means no encoding
                }
            )
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                print(f"Success! elements count: {len(resp.json().get('elements', []))}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test())
