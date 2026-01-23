import asyncio
import aiosqlite

async def inspect():
    print("🕵️ Inspecting Local DB for 'Xoah-Lin Oda — Character Hub'...")
    async with aiosqlite.connect("veillore.db") as db:
        db.row_factory = aiosqlite.Row
        target = "2e5ca671-311e-81e2-ae43-d3d78b3881ad"
        async with db.execute("SELECT * FROM entities WHERE notion_id = ?", (target,)) as cursor:
            row = await cursor.fetchone()
            if row:
                print(f"✅ Found in DB! Score: {row['score']} | Last Edited: {row['last_edited']}")
            else:
                print("❌ NOT FOUND in local DB.")

if __name__ == "__main__":
    asyncio.run(inspect())
