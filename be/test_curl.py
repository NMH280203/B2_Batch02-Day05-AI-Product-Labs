import subprocess
import json

def test_curl():
    url = "https://overpass-api.de/api/interpreter"
    query = """
    [out:json];
    (
      node(around:1500,10.7769,106.7009)[amenity=restaurant];
    );
    out body 5;
    """
    
    print("Testing curl POST request...")
    try:
        # Run curl via subprocess
        # curl -d "data=..." URL
        cmd = [
            "curl",
            "-s",
            "--data-urlencode", f"data={query}",
            url
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        print(f"Curl Exit Code: {res.returncode}")
        print(f"Curl stdout length: {len(res.stdout)}")
        print(f"Curl stderr: {res.stderr}")
        if res.returncode == 0 and res.stdout:
            try:
                data = json.loads(res.stdout)
                print(f"Curl Success! Elements count: {len(data.get('elements', []))}")
                if data.get('elements'):
                    print(f"First element: {data['elements'][0].get('tags', {}).get('name')}")
            except Exception as pe:
                print(f"JSON Parse error: {pe}")
                print(f"Raw Output start: {res.stdout[:500]}")
    except Exception as e:
        print(f"Curl failed: {e}")

if __name__ == "__main__":
    test_curl()
