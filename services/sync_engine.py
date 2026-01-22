import asyncio
import os
from typing import Dict, Any, List
from services.notion import NotionService
from services.memory import LoreMemoryService
import httpx

class LoreSyncEngine:
    """
    Differential Sync Engine.
    Pulls updates from Notion and populates local SQLite memory.
    """
    
    def __init__(self):
        self.notion = NotionService()
        self.memory = LoreMemoryService()

    async def run_sync(self):
        """Executes a full or differential sync."""
        await self.memory.initialize()
        stats = await self.memory.get_stats()
        last_sync_time = stats.get("last_notion_edit")
        
        print(f"🔄 LoreSync: Starting sync. Last edit in DB: {last_sync_time}")
        
        try:
            all_pages = await self._fetch_all_notion_pages()
            print(f"🔄 LoreSync: Found {len(all_pages)} pages in Notion.")
        except Exception as e:
            print(f"❌ LoreSync: Failed to fetch pages from Notion: {e}")
            return

        updated_count = 0
        for page in all_pages:
            try:
                notion_edit = page.get("last_edited_time")
                page_id = page["id"]
                name = self._get_title(page)
                
                print(f"   -> Processing ({updated_count+1}/{len(all_pages)}): {name}...")
                
                # Fetch full content for the page
                content = await self._fetch_page_content(page_id)
                
                entity_data = {
                    "notion_id": page_id,
                    "name": name,
                    "category": self._get_select(page, "Category"),
                    "description": self._get_rich_text(page, "Description"),
                    "era": self._get_select(page, "Universe Era"),
                    "content": content,
                    "last_edited": notion_edit,
                    "url": page.get("url")
                }
                
                await self.memory.upsert_entity(entity_data)
                updated_count += 1
                
                # Small sleep to be nice to the API
                await asyncio.sleep(0.1)
                
            except Exception as e:
                print(f"   ⚠️ LoreSync: Failed to process page {page.get('id')}: {e}")
            
        print(f"✅ LoreSync: Sync complete. Updated {updated_count} entities.")

    async def _fetch_all_notion_pages(self) -> List[Dict[str, Any]]:
        url = f"https://api.notion.com/v1/databases/{self.notion.DATABASE_ID}/query"
        headers = {
            "Authorization": f"Bearer {self.notion.token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        
        pages = []
        has_more = True
        next_cursor = None
        
        timeout = httpx.Timeout(30.0, connect=60.0)
        
        while has_more:
            payload = {"page_size": 100}
            if next_cursor:
                payload["start_cursor"] = next_cursor
                
            async with httpx.AsyncClient(timeout=timeout) as http:
                response = await http.post(url, json=payload, headers=headers)
                response.raise_for_status()
            
            data = response.json()
            pages.extend(data.get("results", []))
            has_more = data.get("has_more", False)
            next_cursor = data.get("next_cursor")
            
        return pages

    async def _fetch_page_content(self, page_id: str) -> str:
        """Fetches and flattens all blocks from a page."""
        url = f"https://api.notion.com/v1/blocks/{page_id}/children"
        headers = {
            "Authorization": f"Bearer {self.notion.token}",
            "Notion-Version": "2022-06-28"
        }
        
        timeout = httpx.Timeout(20.0, connect=30.0)
        content_parts = []
        
        try:
            async with httpx.AsyncClient(timeout=timeout) as http:
                response = await http.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    for block in data.get("results", []):
                        btype = block.get("type")
                        if btype == "paragraph":
                            text = "".join([t.get("plain_text", "") for t in block["paragraph"].get("rich_text", [])])
                            content_parts.append(text)
                        elif btype == "toggle":
                            text = "".join([t.get("plain_text", "") for t in block["toggle"].get("rich_text", [])])
                            content_parts.append(f"\n{text}")
                        elif btype.startswith("heading"):
                            text = "".join([t.get("plain_text", "") for t in block[btype].get("rich_text", [])])
                            content_parts.append(f"\n{text}")
        except Exception as e:
            print(f"      ⚠️ Content fetch error for {page_id}: {e}")
            
        return "\n".join(content_parts)

    def _get_title(self, page):
        props = page.get("properties", {})
        title_objs = props.get("Name", {}).get("title", [])
        return title_objs[0]["plain_text"] if title_objs else "Untitled"

    def _get_select(self, page, prop_name):
        props = page.get("properties", {})
        obj = props.get(prop_name, {}).get("select")
        return obj["name"] if obj else "Unknown"

    def _get_rich_text(self, page, prop_name):
        props = page.get("properties", {})
        objs = props.get(prop_name, {}).get("rich_text", [])
        return objs[0]["plain_text"] if objs else ""

if __name__ == "__main__":
    engine = LoreSyncEngine()
    asyncio.run(engine.run_sync())
