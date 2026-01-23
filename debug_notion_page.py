import asyncio
import os
from services.notion import NotionService

async def debug_page():
    notion = NotionService()
    target_id = "2e5ca671-311e-81e2-ae43-d3d78b3881ad"
    print(f"🔍 Inspecting specific Page ID: {target_id}...")
    
    import httpx
    url = f"https://api.notion.com/v1/pages/{target_id}"
    headers = {
        "Authorization": f"Bearer {notion.token}",
        "Notion-Version": "2022-06-28",
    }
    async with httpx.AsyncClient() as http:
        resp = await http.get(url, headers=headers)
        if resp.status_code != 200:
            print(f"❌ Failed to fetch page: {resp.status_code} {resp.text}")
            return

        data = resp.json()
        props = data.get("properties", {})
        
        name_title = props.get("Name", {}).get("title", [])
        name = name_title[0]["plain_text"] if name_title else "Untitled"
        
        parent = data.get("parent", {})
        parent_type = parent.get("type")
        parent_id = parent.get(parent_type)
        
        score = props.get("Importance Score", {}).get("number")
        
        print(f"\n📄 Found: {name}")
        print(f"   ID: {data['id']}")
        print(f"   Parent Type: {parent_type}")
        print(f"   Parent ID: {parent_id}")
        print(f"   Expected DB ID: {notion.DATABASE_ID}")
        print(f"   ⭐ Importance Score: {score}")
        
        if parent_type == "database_id" and parent_id.replace("-", "") == notion.DATABASE_ID.replace("-", ""):
            print("✅ Page IS in the correct database.")
        else:
            print("⚠️ Page is NOT in the configured database!")

    await notion.close()

if __name__ == "__main__":
    asyncio.run(debug_page())
