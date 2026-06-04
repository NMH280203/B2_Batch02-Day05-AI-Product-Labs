import asyncio
import sys
from services import places as places_service

# Reset stdout to force utf-8 on Windows command line
sys.stdout.reconfigure(encoding='utf-8')

async def test():
    print("=== TESTING REAL OVERPASS API (OSM) ===")
    
    # District 1, HCMC Coordinates
    lat, lng = 10.7769, 106.7009
    query = "pho"
    radius = 1500 # 1.5 km
    
    print(f"Searching for '{query}' near: ({lat}, {lng}) within {radius}m...")
    
    try:
        results = await places_service.search(lat, lng, query, radius)
        
        print(f"\nFound {len(results)} results:")
        for i, r in enumerate(results, 1):
            source_type = "OpenStreetMap" if r["place_id"].startswith("osm_") else "Mock Data (Fallback)"
            print(f"{i}. [{source_type}] {r['name']}")
            print(f"   Address: {r['address']}")
            print(f"   Distance: {r['distance_km']} km")
            print(f"   Google Maps Link: {r['maps_url']}")
            print("-" * 50)
            
        if results and results[0]["place_id"].startswith("osm_"):
            print("\n[Detail] Fetching details for first venue...")
            detail_res = await places_service.detail(results[0]["place_id"])
            if detail_res:
                print(f"Name: {detail_res.get('name')}")
                print(f"Phone: {detail_res.get('formatted_phone_number')}")
                print(f"Address: {detail_res.get('formatted_address')}")
            else:
                print("Could not fetch detail.")
                
    except Exception as e:
        print(f"Error executing search: {e}")

if __name__ == "__main__":
    asyncio.run(test())
