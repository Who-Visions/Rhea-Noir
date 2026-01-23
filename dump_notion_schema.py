import asyncio
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

DATABASE_ID = "2e5ca671-311e-811f-b3d7-c7f3b9150afe"
TOKEN = os.getenv("NOTION_TOKEN")

async def dump_schema():
    if not TOKEN:
        print("❌ Error: NOTION_TOKEN not found.")
        return

    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            props = data.get("properties", {})
            print(f"✅ Database Schema: {len(props)} properties found.")
            print("--------------------------------------------------")
            for name, details in props.items():
                dtype = details.get("type")
                print(f"🔹 {name} ({dtype})")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    asyncio.run(dump_schema())
