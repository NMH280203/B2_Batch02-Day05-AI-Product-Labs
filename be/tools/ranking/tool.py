import sys


def _normalize(values: list[float]) -> list[float]:
    """Normalize list về 0–1."""
    if not values:
        return values
    mn, mx = min(values), max(values)
    if mx == mn:
        return [1.0] * len(values)
    return [(v - mn) / (mx - mn) for v in values]


async def handle(tool_input: dict) -> dict:
    """
    Tính score và xếp hạng quán ăn.
    Score = food_match*0.3 + rating*0.25 + (1-distance)*0.2 + (1-price)*0.15 + reviews*0.1
    """
    try:
        restaurants_raw = tool_input.get("restaurants", [])
        if not isinstance(restaurants_raw, list):
            return {"restaurants": []}
            
        restaurants: list[dict] = [r for r in restaurants_raw if isinstance(r, dict)]
        if not restaurants:
            return {"restaurants": []}

        food_names_raw = tool_input.get("food_names", [])
        if not isinstance(food_names_raw, list):
            food_names_raw = []
        food_names: list[str] = [str(f).lower() for f in food_names_raw if f]

        try:
            top_n = int(tool_input.get("top_n", 5))
            if top_n <= 0:
                top_n = 5
        except (ValueError, TypeError):
            top_n = 5

        # Tính food_match score
        def food_match_score(r: dict) -> float:
            dishes = [d.lower() for d in r.get("featured_dishes", [])]
            name_lower = r.get("name", "").lower()
            if not food_names:
                return 0.5
            matches = sum(
                1 for food in food_names
                if any(food in dish for dish in dishes) or food in name_lower
            )
            return min(1.0, matches / len(food_names))

        # Extract raw values
        ratings = [float(r.get("rating", 4.0)) for r in restaurants]
        distances = [float(r.get("distance_km", 1.0)) for r in restaurants]
        prices = [float(r.get("price_level", 2)) for r in restaurants]
        review_counts = [float(r.get("user_ratings_total", 100)) for r in restaurants]
        food_matches = [food_match_score(r) for r in restaurants]

        # Normalize
        norm_ratings = _normalize(ratings)
        norm_distances = _normalize(distances)  # sẽ đảo (gần hơn = tốt hơn)
        norm_prices = _normalize(prices)  # sẽ đảo (rẻ hơn = tốt hơn)
        norm_reviews = _normalize(review_counts)

        # Tính final score
        scored = []
        for i, r in enumerate(restaurants):
            score = (
                food_matches[i] * 0.30
                + norm_ratings[i] * 0.25
                + (1 - norm_distances[i]) * 0.20
                + (1 - norm_prices[i]) * 0.15
                + norm_reviews[i] * 0.10
            )
            r_copy = dict(r)
            r_copy["score"] = round(score, 4)
            scored.append(r_copy)

        # Sort DESC, lấy top_n
        scored.sort(key=lambda x: x["score"], reverse=True)
        return {"restaurants": scored[:top_n]}

    except Exception as e:
        print(f"[ERROR] ranking handler failed: {e}", file=sys.stderr)
        return {"restaurants": tool_input.get("restaurants", [])[:5]}
