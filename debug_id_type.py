import os
import asyncio
from notion_client import AsyncClient
from dotenv import load_dotenv

load_dotenv()

async def main():
    token = os.environ.get("NOTION_TOKEN")
    # Formatted ID from user link
    target_id = "2e5ca671-311e-811f-b3d7-c7f3b9150afe"
    
    notion = AsyncClient(auth=token)
    
    print(f"Testing ID: {target_id}")
    
    # Try as Database
    try:
        print("[1] Trying databases.retrieve...")
        db = await notion.databases.retrieve(target_id)
        print(f"✅ Success! It is a Database: {db.get('title', 'No Title')}")
        return
    except Exception as e:
        print(f"❌ Not a Database: {e}")

    # Try as Page
    try:
        print("[2] Trying pages.retrieve...")
        page = await notion.pages.retrieve(target_id)
        print(f"✅ Success! It is a Page: {page.get('id')}")
    except Exception as e:
        print(f"❌ Not a Page either: {e}")

if __name__ == "__main__":
    asyncio.run(main())
