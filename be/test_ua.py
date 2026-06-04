import asyncio
import httpx

async def test():
    url = "https://lz4.overpass-api.de/api/interpreter"
    
    query = '[out:json];node(around:1500,10.7769,106.7009)[amenity=restaurant];out body 5;'
    
    # Clean, identifiable User-Agent that doesn't fake standard browsers
    headers = {
        "User-Agent": "Day05AIProductLabsFoodBot/1.0 (contact@myaiplatformvn.com)",
        "Accept": "application/json"
    }
    
    print("Testing clean custom User-Agent...")
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, data={"data": query}, headers=headers)
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                print(f"Success! Elements found: {len(resp.json().get('elements', []))}")
                print(f"First element name: {resp.json().get('elements')[0].get('tags', {}).get('name')}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test())
