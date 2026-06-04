import httpx
import asyncio
import json

async def main():
    payload = {
        "messages": [
            {"role": "user", "content": "tìm quanh khu vực của tôi cho tôi"}
        ],
        "context": {
            "location": {"lat": 10.7769, "lng": 106.7009, "address": "Quận 1, TP. HCM"},
            "budget": None,
            "people": None,
            "meal_time": None,
            "purpose": None,
            "preferences": [],
            "allergies": []
        }
    }
    async with httpx.AsyncClient(timeout=30) as client:
        print("Sending request to /api/chat...")
        try:
            async with client.stream("POST", "http://localhost:8000/api/chat", json=payload) as response:
                print(f"Status code: {response.status_code}")
                async for line in response.iter_lines():
                    if line:
                        print(line)
        except Exception as e:
            print(f"Error calling API: {e}")

if __name__ == "__main__":
    asyncio.run(main())
