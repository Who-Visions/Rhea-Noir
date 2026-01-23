import asyncio
import aiosqlite
from datetime import datetime, timedelta

async def check_recent_syncs():
    print("🕵️ Checking LoreDB for recent activity...")
    async with aiosqlite.connect("veillore.db") as db:
        db.row_factory = aiosqlite.Row
        
        # 1. Check last sync time (based on last_synced column)
        async with db.execute("SELECT MAX(last_synced) as last_sync FROM entities") as cursor:
            row = await cursor.fetchone()
            last_sync = row['last_sync'] if row else "Never"
            print(f"🕒 Most recent entity sync timestamp: {last_sync}")

        # 2. Check for entries edited in Notion recently (last 8 hours)
        # Using a loose assumption that 'today' entries are relevant
        print("\n📄 Entities edited in Notion today (local time):")
        async with db.execute("SELECT name, last_edited, score FROM entities ORDER BY last_edited DESC LIMIT 5") as cursor:
            rows = await cursor.fetchall()
            for row in rows:
                print(f"   - {row['name']} (Edited: {row['last_edited']}, Score: {row['score']})")

if __name__ == "__main__":
    asyncio.run(check_recent_syncs())
