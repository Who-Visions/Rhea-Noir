
import asyncio
from rhea_noir.search import RheaSearch

async def test_lore_search():
    print("\n--- Testing Lore Search Integration ---")
    searcher = RheaSearch()
    # Ensure DB value schema is updated
    await searcher.lore_memory.initialize()
    
    # 1. Test direct lore search
    query = "Xoah"
    print(f"Querying Lore for: '{query}'")
    results = await searcher.search_lore(query)
    
    if results:
        print(f"✅ Found {len(results)} lore entries.")
        for r in results:
            print(f"   - {r.get('name')}: {r.get('description')[:50]}...")
    else:
        print("⚠️ No lore entries found (expected if DB is empty or not synced yet).")

    # 2. Test unified search priority
    print(f"\nQuerying Unified Search for: '{query}'")
    unified = await searcher.unified_search_async(query)
    
    if "lore" in unified and unified["lore"]:
        print("✅ 'lore' results present in unified search.")
    else:
        print("⚠️ 'lore' results missing from unified search.")
        
    if "web" in unified:
         print(f"ℹ️ Web results count: {len(unified['web'])}")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(test_lore_search())
