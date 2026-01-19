import os
import asyncio
from notion_client import AsyncClient
from dotenv import load_dotenv

load_dotenv()

async def main():
    token = os.environ.get("NOTION_TOKEN")
    print(f"Token: {token[:5]}...")
    
    notion = AsyncClient(auth=token)
    
    print("Searching for databases...")
    try:
        # Search all (filter removed to avoid validation error)
        results = await notion.search()
        print(f"Found {len(results['results'])} databases.")
        for db in results['results']:
            print(f" - {db['title'][0]['plain_text'] if db['title'] else 'Untitled'} (ID: {db['id']})")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
