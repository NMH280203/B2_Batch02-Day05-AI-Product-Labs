from services import places as places_service


async def handle_search(tool_input: dict) -> dict:
    """
    Tìm quán ăn gần user.
    """
    try:
        lat = float(tool_input.get("lat", 10.7769))
        lng = float(tool_input.get("lng", 106.7009))
        if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            lat, lng = 10.7769, 106.7009
    except (ValueError, TypeError):
        lat, lng = 10.7769, 106.7009

    query = str(tool_input.get("query", "quán ăn")).strip()
    if not query:
        query = "quán ăn"

    try:
        radius = int(tool_input.get("radius", 2000))
        if radius <= 0 or radius > 50000:
            radius = 2000
    except (ValueError, TypeError):
        radius = 2000

    budget = tool_input.get("budget")
    if budget is not None:
        try:
            budget = int(budget)
            if budget <= 0:
                budget = None
        except (ValueError, TypeError):
            budget = None

    restaurants = await places_service.search(lat, lng, query, radius, budget)
    return {"restaurants": restaurants}


async def handle_detail(tool_input: dict) -> dict:
    """
    Lấy chi tiết 1 quán.
    """
    place_id = str(tool_input.get("place_id", ""))
    result = await places_service.detail(place_id)
    return {"detail": result} if result else {"detail": None}
