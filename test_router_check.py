import os
from dotenv import load_dotenv
from rhea_noir.gemini3_router import get_router

load_dotenv()

def test_router():
    router = get_router()
    
    # Test 1: Simple query (should be Flash)
    decision = router.route("Hi Rhea")
    print(f"Simple Query Decision: {decision}")
    
    # Test 2: Complex query (should be Pro/Parallel)
    decision = router.route("Can you analyze the architecture of the Watchdog skill and explain how it integrates with Vertex AI Reasoning Engine?")
    print(f"Complex Query Decision: {decision}")
    
    # Test 3: Search query (should be Search model)
    decision = router.route("What is the latest news about Gemini 3?")
    print(f"Search Query Decision: {decision}")

if __name__ == "__main__":
    try:
        test_router()
    except Exception as e:
        print(f"Router Test Failed: {e}")
