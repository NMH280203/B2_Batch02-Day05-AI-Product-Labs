from fastapi import APIRouter, Query
from services import places as places_service
from tools.ranking import tool as ranking_handler

router = APIRouter()


@router.get("/restaurants")
async def get_restaurants(
    lat: float = Query(..., description="Vĩ độ"),
    lng: float = Query(..., description="Kinh độ"),
    query: str = Query("quán ăn", description="Từ khóa tìm kiếm"),
    budget: int | None = Query(None, description="Ngân sách (VND)"),
    radius: int = Query(2000, description="Bán kính (mét)"),
    limit: int = Query(5, description="Số quán trả về"),
):
    """
    Tìm quán ăn gần vị trí chỉ định.
    """
    restaurants = await places_service.search(lat, lng, query, radius, budget)

    if restaurants:
        ranked = await ranking_handler.handle({
            "restaurants": restaurants,
            "food_names": query.split(),
            "top_n": limit,
        })
        restaurants = ranked.get("restaurants", restaurants[:limit])
    else:
        restaurants = restaurants[:limit]

    return {
        "restaurants": restaurants,
        "total": len(restaurants),
        "query_used": query,
    }
