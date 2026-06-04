import os
import sys
import httpx
from dotenv import load_dotenv

load_dotenv(override=True)

OPENWEATHER_KEY = os.getenv("OPENWEATHER_API_KEY", "")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


async def get_weather(lat: float, lng: float) -> dict:
    """
    Gọi OpenWeatherMap API.
    Fallback trả condition='normal' nếu thiếu key hoặc lỗi.
    """
    if not OPENWEATHER_KEY:
        return {"condition": "normal", "temp_c": 30.0, "description": "Thời tiết bình thường"}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                BASE_URL,
                params={
                    "lat": lat,
                    "lon": lng,
                    "appid": OPENWEATHER_KEY,
                    "units": "metric",
                    "lang": "vi",
                },
            )
            resp.raise_for_status()
            data = resp.json()

        temp = data["main"]["temp"]
        weather_id = data["weather"][0]["id"]
        description = data["weather"][0]["description"]

        # Map điều kiện thời tiết
        if 500 <= weather_id < 600:
            condition = "rainy"
        elif temp > 32:
            condition = "hot"
        elif temp < 20:
            condition = "cold"
        else:
            condition = "normal"

        return {"condition": condition, "temp_c": round(temp, 1), "description": description}

    except Exception as e:
        print(f"[ERROR] Weather API failed: {e}", file=sys.stderr)
        return {"condition": "normal", "temp_c": 30.0, "description": "Không lấy được thông tin thời tiết"}
