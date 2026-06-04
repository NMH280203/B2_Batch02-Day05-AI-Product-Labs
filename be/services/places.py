import os
import sys
import math
import httpx
from dotenv import load_dotenv

load_dotenv(override=True)

_raw_key = os.getenv("GOOGLE_PLACES_API_KEY", "")
# Bỏ qua nếu là placeholder chưa điền thật
PLACES_KEY = _raw_key if _raw_key and not _raw_key.startswith("your-") else ""
OVERPASS_URL = "https://lz4.overpass-api.de/api/interpreter"
USER_AGENT = "Day05AIProductLabsFoodBot/1.0 (contact@myaiplatformvn.com)"

MOCK_RESTAURANTS = [
    {
        "place_id": "mock_001",
        "name": "Cơm Tấm Thuận Kiều",
        "address": "123 Nguyễn Trãi, Q.1, TP.HCM",
        "distance_km": 0.3,
        "rating": 4.5,
        "price_level": 2,
        "is_open": True,
        "phone": "028-1234-5678",
        "maps_url": "https://maps.google.com/?q=C%C6%A1m+T%E1%BA%A5m+Thu%E1%BA%ADn+Ki%E1%BB%81u+Q1+TPHCM",
        "photo_url": None,
        "featured_dishes": ["Cơm tấm sườn", "Cơm tấm bì chả", "Bì cuốn"],
        "score": 0.85,
        "user_ratings_total": 320,
    },
    {
        "place_id": "mock_002",
        "name": "Phở Hà Nội Ngon",
        "address": "45 Lê Lợi, Q.1, TP.HCM",
        "distance_km": 0.7,
        "rating": 4.2,
        "price_level": 2,
        "is_open": True,
        "phone": "028-9876-5432",
        "maps_url": "https://maps.google.com/?q=Ph%E1%BB%9F+H%C3%A0+N%E1%BB%99i+Ngon+Q1+TPHCM",
        "photo_url": None,
        "featured_dishes": ["Phở bò tái", "Phở gà", "Phở đặc biệt"],
        "score": 0.80,
        "user_ratings_total": 210,
    },
    {
        "place_id": "mock_003",
        "name": "Bún Bò Huế Mợ Tư",
        "address": "88 Đinh Tiên Hoàng, Q.Bình Thạnh, TP.HCM",
        "distance_km": 1.2,
        "rating": 4.7,
        "price_level": 1,
        "is_open": True,
        "phone": None,
        "maps_url": "https://maps.google.com/?q=B%C3%BAn+B%C3%B2+Hu%E1%BA%BF+M%E1%BB%A3+T%C6%B0+Binh+Thanh",
        "photo_url": None,
        "featured_dishes": ["Bún bò Huế đặc biệt", "Bún bò chả cua", "Bánh mì"],
        "score": 0.90,
        "user_ratings_total": 480,
    },
    {
        "place_id": "mock_004",
        "name": "Bánh Mì 37 Nguyễn Trãi",
        "address": "37 Nguyễn Trãi, Q.1, TP.HCM",
        "distance_km": 0.5,
        "rating": 4.4,
        "price_level": 1,
        "is_open": True,
        "phone": "028-3333-7777",
        "maps_url": "https://maps.google.com/?q=Banh+Mi+37+Nguyen+Trai+Q1",
        "photo_url": None,
        "featured_dishes": ["Bánh mì thịt", "Bánh mì gà nướng", "Bánh mì bì"],
        "score": 0.78,
        "user_ratings_total": 550,
    },
    {
        "place_id": "mock_005",
        "name": "Lẩu Nướng 5 Sao",
        "address": "200 Pasteur, Q.3, TP.HCM",
        "distance_km": 1.8,
        "rating": 4.3,
        "price_level": 3,
        "is_open": True,
        "phone": "028-5555-8888",
        "maps_url": "https://maps.google.com/?q=Lau+Nuong+5+Sao+Pasteur+Q3",
        "photo_url": None,
        "featured_dishes": ["Lẩu thái", "Lẩu mắm", "Nướng BBQ", "Hải sản"],
        "score": 0.75,
        "user_ratings_total": 890,
    },
    {
        "place_id": "mock_006",
        "name": "Chay Thiện Duyên",
        "address": "56 Võ Thị Sáu, Q.3, TP.HCM",
        "distance_km": 1.5,
        "rating": 4.6,
        "price_level": 2,
        "is_open": True,
        "phone": None,
        "maps_url": "https://maps.google.com/?q=Chay+Thien+Duyen+Vo+Thi+Sau+Q3",
        "photo_url": None,
        "featured_dishes": ["Cơm chay", "Bún chay", "Phở chay", "Bánh cuốn chay"],
        "score": 0.88,
        "user_ratings_total": 270,
    },
    {
        "place_id": "mock_007",
        "name": "Cơm Gà Hải Nam Đông Nguyên",
        "address": "301 Nguyễn Trãi, Q.5, TP.HCM",
        "distance_km": 2.1,
        "rating": 4.4,
        "price_level": 2,
        "is_open": True,
        "phone": "028-3855-7788",
        "maps_url": "https://maps.google.com/?q=Com+Ga+Dong+Nguyen+Nguyen+Trai+Q5",
        "photo_url": None,
        "featured_dishes": ["Cơm gà luộc", "Cơm gà xối mỡ", "Canh cải cải bắc"],
        "score": 0.82,
        "user_ratings_total": 410,
    },
    {
        "place_id": "mock_008",
        "name": "Bún Riêu Gánh Bến Thành",
        "address": "4 Phan Bội Châu, Q.1, TP.HCM",
        "distance_km": 0.6,
        "rating": 4.3,
        "price_level": 2,
        "is_open": True,
        "phone": None,
        "maps_url": "https://maps.google.com/?q=Bun+Rieu+Ganh+Ben+Thanh",
        "photo_url": None,
        "featured_dishes": ["Bún riêu cua đặc biệt", "Bún riêu chả cá"],
        "score": 0.81,
        "user_ratings_total": 650,
    },
    {
        "place_id": "mock_009",
        "name": "Hủ Tiếu Nam Vang Nhân Quán",
        "address": "122 Nguyễn Thị Minh Khai, Q.3, TP.HCM",
        "distance_km": 1.1,
        "rating": 4.5,
        "price_level": 2,
        "is_open": True,
        "phone": "028-3930-1122",
        "maps_url": "https://maps.google.com/?q=Hu+Tieu+Nam+Vang+Nhan+Quan+Q3",
        "photo_url": None,
        "featured_dishes": ["Hủ tiếu khô đặc biệt", "Hủ tiếu nước"],
        "score": 0.87,
        "user_ratings_total": 520,
    },
    {
        "place_id": "mock_010",
        "name": "Bánh Xèo Ăn Là Ghiền",
        "address": "74 Sương Nguyệt Ánh, Q.1, TP.HCM",
        "distance_km": 0.9,
        "rating": 4.2,
        "price_level": 2,
        "is_open": True,
        "phone": "028-3925-2525",
        "maps_url": "https://maps.google.com/?q=Banh+Xeo+An+La+Ghien+Suong+Nguyet+Anh",
        "photo_url": None,
        "featured_dishes": ["Bánh xèo tôm nhảy", "Bánh xèo mực", "Bánh khọt"],
        "score": 0.79,
        "user_ratings_total": 380,
    },
    {
        "place_id": "mock_011",
        "name": "Cà Phê Muối Chú Long Q.1",
        "address": "12 Cống Quỳnh, Q.1, TP.HCM",
        "distance_km": 0.4,
        "rating": 4.8,
        "price_level": 1,
        "is_open": True,
        "phone": None,
        "maps_url": "https://maps.google.com/?q=Ca+Phe+Muoi+Chu+Long+Cong+Quynh",
        "photo_url": None,
        "featured_dishes": ["Cà phê muối", "Cà phê bạc xỉu", "Cà phê đen đá"],
        "score": 0.94,
        "user_ratings_total": 1200,
    },
    {
        "place_id": "mock_012",
        "name": "Bún Chả Sinh Từ",
        "address": "33 Nguyễn Huy Tự, Q.1, TP.HCM",
        "distance_km": 1.4,
        "rating": 4.4,
        "price_level": 2,
        "is_open": True,
        "phone": "028-6677-8899",
        "maps_url": "https://maps.google.com/?q=Bun+Cha+Sinh+Tu+Nguyen+Huy+Tu",
        "photo_url": None,
        "featured_dishes": ["Bún chả truyền thống", "Nem hải sản giòn"],
        "score": 0.83,
        "user_ratings_total": 450,
    },
]


def _calc_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Tính khoảng cách Haversine (km)."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


async def search(
    lat: float,
    lng: float,
    query: str,
    radius: int = 2000,
    budget: int | None = None,
) -> list[dict]:
    """Tìm quán ăn gần đây dùng OpenStreetMap Overpass API (Không cần API key)."""
    overpass_query = f"""
    [out:json];
    (
      node(around:{radius},{lat},{lng})[amenity=restaurant];
      node(around:{radius},{lat},{lng})[amenity=cafe];
      node(around:{radius},{lat},{lng})[amenity=fast_food];
    );
    out body;
    """
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json"
    }
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(OVERPASS_URL, data={"data": overpass_query}, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        elements = data.get("elements", [])
        results = []
        for el in elements:
            tags = el.get("tags", {})
            name = tags.get("name", "").strip()
            if not name:
                continue

            # Lọc theo query từ khóa trong python (đáp ứng tìm kiếm linh hoạt tiếng Việt)
            if query and query.lower() not in name.lower() and query.lower() not in tags.get("amenity", "").lower():
                continue

            place_id = f"osm_{el.get('id')}"
            place_lat = el.get("lat", lat)
            place_lng = el.get("lon", lng)
            distance = round(_calc_distance(lat, lng, place_lat, place_lng), 2)

            street = tags.get("addr:street", "")
            housenumber = tags.get("addr:housenumber", "")
            city = tags.get("addr:city", "")
            address = f"{housenumber} {street}".strip()
            if city:
                address += f", {city}"
            if not address:
                address = "Địa chỉ lân cận"

            results.append({
                "place_id": place_id,
                "name": name,
                "address": address,
                "distance_km": distance,
                "rating": 4.2,  # OSM không có rating nên mặc định 4.2
                "price_level": 2,
                "is_open": True,
                "phone": tags.get("phone", tags.get("contact:phone")),
                "maps_url": f"https://www.google.com/maps/place/{place_lat},{place_lng}",
                "photo_url": None,
                "featured_dishes": [],
                "score": 0.0,
                "user_ratings_total": 50,
            })

        # Sắp xếp kết quả theo khoảng cách tăng dần
        results.sort(key=lambda x: x["distance_km"])
        return results[:10] if results else list(MOCK_RESTAURANTS)

    except Exception as e:
        print(f"[ERROR] OSM Overpass search failed: {e}", file=sys.stderr)
        return list(MOCK_RESTAURANTS)


async def detail(place_id: str) -> dict | None:
    """Lấy chi tiết 1 quán theo place_id từ OSM hoặc mock data."""
    if not place_id:
        return None

    if not place_id.startswith("osm_"):
        for mock in MOCK_RESTAURANTS:
            if mock["place_id"] == place_id:
                return {
                    "name": mock["name"],
                    "formatted_address": mock["address"],
                    "formatted_phone_number": mock["phone"],
                    "opening_hours": {"open_now": mock["is_open"]},
                    "rating": mock["rating"],
                    "price_level": mock["price_level"],
                    "photos": [],
                    "geometry": {
                        "location": {
                            "lat": 10.7769,
                            "lng": 106.7009
                        }
                    }
                }
        return None

    osm_id = place_id.replace("osm_", "")
    query_str = f"[out:json];node({osm_id});out body;"
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json"
    }
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(OVERPASS_URL, data={"data": query_str}, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        elements = data.get("elements", [])
        if not elements:
            return None

        node = elements[0]
        tags = node.get("tags", {})
        street = tags.get("addr:street", "")
        housenumber = tags.get("addr:housenumber", "")
        city = tags.get("addr:city", "")
        address = f"{housenumber} {street}".strip()
        if city:
            address += f", {city}"
        if not address:
            address = "Địa chỉ lân cận"

        return {
            "name": tags.get("name", "Quán ăn"),
            "formatted_address": address,
            "formatted_phone_number": tags.get("phone", tags.get("contact:phone")),
            "opening_hours": {"open_now": True},
            "rating": 4.2,
            "price_level": 2,
            "photos": [],
            "geometry": {
                "location": {
                    "lat": node.get("lat"),
                    "lng": node.get("lon")
                }
            }
        }
    except Exception as e:
        print(f"[ERROR] OSM Overpass detail failed: {e}", file=sys.stderr)
        return None


