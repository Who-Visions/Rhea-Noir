import requests
import json

def test_ingest():
    url = "http://localhost:8081/v1/ingest"
    
    # Test 1: Raw Text
    print("Testing Raw Text Ingest...")
    payload_text = {
        "content": "The quick brown fox jumps over the lazy dog. Concept: Speed. Era: Now.",
        "hint": "Test ingest"
    }
    try:
        resp = requests.post(url, json=payload_text)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.json()}")
    except Exception as e:
        print(f"Failed: {e}")

    # Test 2: URL (Youtube - we'll use a known short one or just the url detection trigger)
    # We won't actually fetch a massive video to avoid blocking, but let's test the trigger
    # We can pass a URL and expect the logs to show 'Detected URL'
    # For a real test, let's use the Mark of the Beast one again or a dummy
    print("\nTesting URL Trigger (Mock)...")
    payload_url = {
        "content": "https://www.youtube.com/watch?v=WK4gCHu3H6I", 
        "hint": "Youtube test"
    }
    # Note: This might take a while if it actually runs yt-dlp, so we might skip waiting if it hangs
    # But for verification we just want to know the endpoint is reachable.
    
    # Debug: Check Health
    try:
        print("\nChecking Health...")
        h = requests.get("http://localhost:8081/health")
        print(f"Health: {h.json()}")
    except:
        print("Health Check Failed")

    # Debug: Check OpenAPI
    try:
        print("\nChecking OpenAPI Schema for /v1/ingest...")
        schema = requests.get("http://localhost:8081/openapi.json").json()
        paths = schema.get("paths", {})
        if "/v1/ingest" in paths:
            print("✅ /v1/ingest found in Schema")
        else:
            print("❌ /v1/ingest NOT found in Schema")
            # print keywords to see what is there
            print(f"Routes found: {list(paths.keys())}")
    except Exception as e:
        print(f"OpenAPI Check Failed: {e}")

if __name__ == "__main__":
    test_ingest()
