import asyncio
from rhea_noir.skills.memory.actions import MemorySkill

async def test_memory():
    print("\n--- Testing Memory Skill (Hindsight Notes) ---")
    skill = MemorySkill()
    
    # 1. Create a Note (Reflect)
    print("📝 Creating a test Hindsight Note...")
    result = await skill._reflect(
        task_name="Test Memory Implementation",
        outcome="success",
        what_happened="Implemented HindsightNote model and SQL table.",
        key_lesson="Using separate tables for different memory types improves query performance.",
        root_cause="Need for structured experiential memory.",
        tags=["memory", "test", "confucius"]
    )
    print(f"✅ Result: {result}")
    
    # 2. Recall the Note
    print("\n🔍 Recalling notes with query 'separate tables'...")
    search_res = await skill._recall_notes("separate tables")
    notes = search_res.get("notes", [])
    
    if notes:
        print(f"✅ Found {len(notes)} notes.")
        for n in notes:
            print(f"   - [{n['timestamp']}] {n['task_name']}: {n['key_lesson']}")
    else:
        print("❌ No notes found!")

if __name__ == "__main__":
    asyncio.run(test_memory())
