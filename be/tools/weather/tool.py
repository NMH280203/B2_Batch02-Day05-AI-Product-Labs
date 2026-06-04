from services import weather as weather_service


async def handle(tool_input: dict) -> dict:
    """
    Lấy thời tiết từ OpenWeatherMap.
    Trả về: { condition, temp_c, description }
    """
    try:
        lat = float(tool_input.get("lat", 10.7769))
        lng = float(tool_input.get("lng", 106.7009))
        if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            # Fallback for invalid coordinates
            lat, lng = 10.7769, 106.7009
    except (ValueError, TypeError):
        lat, lng = 10.7769, 106.7009
    return await weather_service.get_weather(lat, lng)
