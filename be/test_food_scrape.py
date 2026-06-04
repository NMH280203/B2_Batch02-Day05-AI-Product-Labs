import asyncio
import sys

sys.stdout.reconfigure(encoding='utf-8')

async def test():
    from tools.food_search.tool import handle

    print("=== Test 1: Lunch, 80k budget ===")
    result = await handle({"meal_time": "lunch", "budget": 80000, "weather": "normal"})
    print(f"Source: {result.get('source', 'unknown')}")
    print(f"Query: {result.get('query', 'N/A')}")
    foods = result.get("foods", [])
    print(f"Foods found: {len(foods)}")
    for f in foods:
        print(f"  - {f['name']} ({f['category']}) ~{f['estimated_price']}d")
        print(f"    Desc: {f['description'][:80]}")
    if result.get("error"):
        print(f"Error: {result['error']}")
    
    print("\n=== Test 2: Scraper trending ===")
    from services.scraper import crawl_trending_foods
    trend_result = await crawl_trending_foods("2025")
    print(f"Source: {trend_result.get('source', 'unknown')}")
    results = trend_result.get("results", [])
    print(f"Results: {len(results)}")
    for r in results[:3]:
        print(f"  -> {r[:100]}")
    if trend_result.get("error"):
        print(f"Error: {trend_result['error']}")

asyncio.run(test())
