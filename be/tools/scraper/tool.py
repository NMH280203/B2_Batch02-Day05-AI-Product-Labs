from services import scraper as scraper_service


async def crawl_trending_foods(tool_input: dict) -> dict:
    query = tool_input.get("query", "")
    return await scraper_service.crawl_trending_foods(query)


async def crawl_restaurant_reviews(tool_input: dict) -> dict:
    restaurant_name = tool_input.get("restaurant_name", "")
    return await scraper_service.crawl_restaurant_reviews(restaurant_name)
