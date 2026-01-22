import os
import asyncio
from typing import List, Optional, Dict, Any
from notion_client import AsyncClient
from models.veilverse import VeilEntity, VeilEvent, VeilLore, VeilVerseCategory, UniverseEra
from dotenv import load_dotenv

load_dotenv()

class NotionService:
    """
    Rhea's interface to the Notion VeilVerse.
    Uses the 'VeilVerse Universe Best' Database ID: 2e5ca671-311e-811f-b3d7-c7f3b9150afe
    """
    
    DATABASE_ID = "2e5ca671-311e-811f-b3d7-c7f3b9150afe"

    def __init__(self):
        self.token = os.getenv("NOTION_TOKEN")
        if not self.token:
            raise ValueError("NOTION_TOKEN not found in environment")
        self.client = AsyncClient(auth=self.token)

    async def fetch_full_database_index(self) -> dict:
        """
        Fetches the Title and ID of EVERY page in the database.
        Handles pagination to ensure 1000+ entries are scanned.
        Returns: dict { "Title Lowercase": "NotionID" }
        """
        import httpx
        url = f"https://api.notion.com/v1/databases/{self.DATABASE_ID}/query"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        
        has_more = True
        next_cursor = None
        full_index = {}
        page_count = 0
        
        print("🧠 Rhea: Starting Full Database Index Scan...")
        
        while has_more:
            payload = {"page_size": 100}
            if next_cursor:
                payload["start_cursor"] = next_cursor
                
            async with httpx.AsyncClient() as http:
                # Retry logic for large scans
                for attempt in range(3):
                    try:
                        response = await http.post(url, json=payload, headers=headers, timeout=30.0)
                        if response.status_code == 200:
                            break
                        await asyncio.sleep(1 * (attempt+1))
                    except Exception:
                        await asyncio.sleep(1)

            if response.status_code != 200:
                print(f"❌ Error Scanning Page {page_count//100}: {response.status_code}")
                break
                
            data = response.json()
            results = data.get("results", [])
            
            for page in results:
                try:
                    props = page.get("properties", {})
                    # Handle different Title property names if schema changes, but usually 'Name'
                    title_prop = props.get("Name", {})
                    if title_prop and "title" in title_prop and title_prop["title"]:
                        title = title_prop["title"][0]["plain_text"]
                        full_index[title.lower().strip()] = page["id"]
                except Exception:
                    continue # Skip malformed pages
            
            page_count += len(results)
            print(f"   ...scanned {page_count} pages...")
            
            has_more = data.get("has_more", False)
            next_cursor = data.get("next_cursor")
            
        print(f"✅ Index Complete. Total Nodes: {len(full_index)}")
        return full_index

    async def search_by_title(self, query: str) -> List[VeilEntity]:
        """
        Uses Notion Search API to find pages by title matching query.
        """
        import httpx
        url = "https://api.notion.com/v1/search"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": query,
            "filter": {
                "value": "page",
                "property": "object"
            },
            "page_size": 20
        }
        
        try:
            async with httpx.AsyncClient() as http:
                response = await http.post(url, json=payload, headers=headers)
                
            if response.status_code != 200:
                print(f"❌ Search Error {response.status_code}: {response.text}")
                return []
                
            data = response.json()
            results = []
            for page in data.get("results", []):
                # Filter by database to ensure it's VeilVerse
                if page.get("parent", {}).get("database_id") == self.DATABASE_ID.replace("-",""): 
                    # Note: Notion API sometimes returns dashless IDs or with dashes, handle carefully.
                    # Actually standardizing checking:
                    pid = page.get("parent", {}).get("database_id")
                    if pid and pid.replace("-","") == self.DATABASE_ID.replace("-",""):
                         entity = self._map_page_to_model(page)
                         if entity: results.append(entity)
            
            return results
        except Exception as e:
            print(f"❌ Search Failed: {e}")
            return []

    async def query_veilverse(self, 
                              category: Optional[VeilVerseCategory] = None, 
                              era: Optional[UniverseEra] = None,
                              limit: int = 10) -> List[VeilEntity]:
        """
        Queries the VeilVerse database using raw httpx to bypass SDK issues.
        """
        import httpx
        
        filter_conditions = []
        if category:
            filter_conditions.append({
                "property": "Category",
                "select": {"equals": category.value}
            })
        if era:
            filter_conditions.append({
                "property": "Universe Era",
                "select": {"equals": era.value}
            })
            
        payload = {
            "page_size": limit,
            "sorts": [
                {
                    "timestamp": "last_edited_time",
                    "direction": "descending"
                }
            ]
        }
        if filter_conditions:
            if len(filter_conditions) == 1:
                payload["filter"] = filter_conditions[0]
            else:
                payload["filter"] = {"and": filter_conditions}

        print(f"🧠 Rhea: Querying Notion (Category={category})...")
        url = f"https://api.notion.com/v1/databases/{self.DATABASE_ID}/query"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": "2022-06-28", # Or latest
            "Content-Type": "application/json"
        }

        try:
            async with httpx.AsyncClient() as http:
                response = await http.post(url, json=payload, headers=headers)
                
            if response.status_code != 200:
                print(f"❌ HTTP Error {response.status_code}: {response.text}")
                return []
                
            data = response.json()
            # print(f"DEBUG: {data.keys()}") 
            
            entities = []
            for page in data.get("results", []):
                entity = self._map_page_to_model(page)
                if entity:
                    entities.append(entity)
            
            print(f"✅ Rhea: Retrieved {len(entities)} entities.")
            return entities
            
        except Exception as e:
            print(f"❌ Notion Query Failed: {e}")
            import traceback
            traceback.print_exc()
            return []

    async def create_entity(self, entity: VeilEntity, content: str = "") -> bool:
        """
        Creates a new page in the VeilVerse database using httpx.
        """
        import httpx
        
        print(f"🧠 Rhea: Creating Notion Page '{entity.name}' ({entity.category})...")
        
        url = "https://api.notion.com/v1/pages"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }

        # Build Properties
        properties = {
            "Name": {"title": [{"text": {"content": entity.name}}]},
        }
        
        if entity.category:
            properties["Category"] = {"select": {"name": entity.category.value}}
        
        if entity.universe_era:
            properties["Universe Era"] = {"select": {"name": entity.universe_era.value}}

        if entity.description:
            properties["Description"] = {"rich_text": [{"text": {"content": entity.description}}]}
        
        if entity.render_status:
            properties["Render Status"] = {"status": {"name": entity.render_status.value}}
            
        if hasattr(entity, "veil_activation_trigger") and entity.veil_activation_trigger:
             properties["Veil Activation Trigger"] = {"rich_text": [{"text": {"content": entity.veil_activation_trigger}}]}

        # Build Icon
        icon_payload = None
        if entity.icon:
            # Simple check: is it an emoji char? (len 1 or 2 usually)
            # Or assume URL if starts with http
            if entity.icon.startswith("http"):
                icon_payload = {"type": "external", "external": {"url": entity.icon}}
            else:
                icon_payload = {"type": "emoji", "emoji": entity.icon}

        # Build Children (Toggle Block for Transcript)
        children = []
        if content:
            # Notion blocks limit is 2000 chars per text block, need chunking if content is huge
            # For simplicity, we create one toggle block with the content chunked inside 
            
            # Simple chunking to avoid 2000 char limit error (Notion API limit)
            # We use 1800 to be safe with unicode/special chars
            chunks = [content[i:i+1800] for i in range(0, len(content), 1800)]
            
            check_text_blocks = []
            for chunk in chunks:
                check_text_blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": chunk}}]
                    }
                })

            children.append({
                "object": "block",
                "type": "toggle",
                "toggle": {
                    "rich_text": [{"type": "text", "text": {"content": "📝 Raw Transcript / Notes"}}],
                    "children": check_text_blocks
                }
            })

        payload = {
            "parent": {"database_id": self.DATABASE_ID},
            "properties": properties,
            "children": children
        }
        
        if icon_payload:
            payload["icon"] = icon_payload

        try:
            async with httpx.AsyncClient() as http:
                response = await http.post(url, json=payload, headers=headers)
                
            if response.status_code != 200:
                print(f"❌ HTTP Error {response.status_code}: {response.text}")
                return False
                
            data = response.json()
            print(f"✅ Created Page ID: {data['id']}")
            return True
        except Exception as e:
            print(f"❌ Page Creation Failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    async def update_page(self, page_id: str, properties: Dict[str, Any], content: Optional[str] = None) -> bool:
        """
        Updates an existing page's properties and appends content if provided.
        """
        import httpx
        print(f"🧠 Rhea: Updating Notion Page ID {page_id}...")
        
        url = f"https://api.notion.com/v1/pages/{page_id}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }

        payload = {"properties": properties}
        
        try:
            async with httpx.AsyncClient() as http:
                response = await http.patch(url, json=payload, headers=headers)
            
            if response.status_code != 200:
                print(f"❌ HTTP Error {response.status_code}: {response.text}")
                return False

            # If there's content to append, we use the blocks endpoint
            if content:
                await self.append_content(page_id, content)
            
            return True
        except Exception as e:
            print(f"❌ Page Update Failed: {e}")
            return False

    async def append_content(self, page_id: str, content: str) -> bool:
        """Appends new blocks to a page."""
        import httpx
        url = f"https://api.notion.com/v1/blocks/{page_id}/children"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        
        chunks = [content[i:i+1800] for i in range(0, len(content), 1800)]
        children = []
        for chunk in chunks:
            children.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": chunk}}]
                }
            })
            
        payload = {"children": children}
        async with httpx.AsyncClient() as http:
            response = await http.patch(url, json=payload, headers=headers)
        return response.status_code == 200

    async def delete_page(self, page_id: str) -> bool:
        """Archives a page (Notion's version of delete)."""
        import httpx
        url = f"https://api.notion.com/v1/pages/{page_id}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        payload = {"archived": True}
        async with httpx.AsyncClient() as http:
            response = await http.patch(url, json=payload, headers=headers)
        return response.status_code == 200

    async def retrieve_blocks(self, block_id: str) -> List[Dict[str, Any]]:
        """Retrieves children blocks of a page or block."""
        import httpx
        url = f"https://api.notion.com/v1/blocks/{block_id}/children"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": "2022-06-28"
        }
        
        results = []
        has_more = True
        next_cursor = None
        
        try:
            async with httpx.AsyncClient() as http:
                while has_more:
                    params = {"page_size": 100}
                    if next_cursor:
                        params["start_cursor"] = next_cursor
                    
                    response = await http.get(url, headers=headers, params=params)
                    if response.status_code != 200:
                        print(f"❌ Block Retrieval Error: {response.status_code}")
                        break
                    
                    data = response.json()
                    results.extend(data.get("results", []))
                    has_more = data.get("has_more", False)
                    next_cursor = data.get("next_cursor")
            return results
        except Exception as e:
            print(f"❌ Error Retrieving Blocks: {e}")
            return []

    async def add_comment(self, page_id: str, text: str, discussion_id: Optional[str] = None) -> bool:
        """Adds a comment to a page or block."""
        import httpx
        url = "https://api.notion.com/v1/comments"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        
        payload = {
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": text}
                }
            ]
        }
        
        if discussion_id:
            payload["discussion_id"] = discussion_id
        else:
            payload["parent"] = {"page_id": page_id}
            
        try:
            async with httpx.AsyncClient() as http:
                response = await http.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                print(f"✅ Comment Added to {page_id}")
                return True
            else:
                print(f"❌ Comment Failed ({response.status_code}): {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error Adding Comment: {e}")
            return False

    async def retrieve_comments(self, block_id: str) -> List[Dict[str, Any]]:
        """Retrieves comments for a page or block."""
        import httpx
        url = f"https://api.notion.com/v1/comments?block_id={block_id}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": "2022-06-28"
        }
        
        results = []
        has_more = True
        next_cursor = None
        
        try:
            async with httpx.AsyncClient() as http:
                while has_more:
                    params = {"page_size": 100}
                    if next_cursor:
                        params["start_cursor"] = next_cursor
                    
                    response = await http.get(url, headers=headers, params=params)
                    if response.status_code != 200:
                        print(f"❌ Comment Retrieval Error: {response.status_code}")
                        break
                    
                    data = response.json()
                    results.extend(data.get("results", []))
                    has_more = data.get("has_more", False)
                    next_cursor = data.get("next_cursor")
            return results
        except Exception as e:
            print(f"❌ Error Retrieving Comments: {e}")
            return []

    # Removed _execute_query helper as we are using httpx directly now

    def _map_page_to_model(self, page: Dict[str, Any]) -> Optional[VeilEntity]:
        """Maps a raw Notion Page to a VeilEntity."""
        try:
            props = page.get("properties", {})
            
            # Helper to safely get Name
            name_prop = props.get("Name", {})
            title_objs = name_prop.get("title", [])
            if not title_objs: return None # Skip empty rows
            name = title_objs[0]["plain_text"]

            # Category
            cat_obj = props.get("Category", {}).get("select")
            category = VeilVerseCategory(cat_obj["name"]) if cat_obj else None
            
            # Era
            era_obj = props.get("Universe Era", {}).get("select")
            era = UniverseEra(era_obj["name"]) if era_obj else None

            # Description
            desc_objs = props.get("Description", {}).get("rich_text", [])
            description = desc_objs[0]["plain_text"] if desc_objs else ""

            # Icon (Emoji or URL)
            icon = None
            icon_obj = page.get("icon")
            if icon_obj:
                icon_type = icon_obj.get("type")
                if icon_type == "emoji":
                    icon = icon_obj.get("emoji")
                elif icon_type == "external":
                    icon = icon_obj.get("external", {}).get("url")
                elif icon_type == "file":
                    icon = icon_obj.get("file", {}).get("url")

            data = {
                "notion_id": page["id"],
                "name": name,
                "description": description,
                "category": category,
                "universe_era": era,
                "url": page.get("url"),
                "icon": icon
            }

            # Polymorphism
            if category == VeilVerseCategory.EVENT:
                date_obj = props.get("Timeline Year", {}).get("number")
                data["event_date"] = str(date_obj) if date_obj else None
                return VeilEvent(**data)
            
            elif category in [VeilVerseCategory.LORE, VeilVerseCategory.CHARACTER]:
                trigger_objs = props.get("Veil Activation Trigger", {}).get("rich_text", [])
                data["veil_activation_trigger"] = trigger_objs[0]["plain_text"] if trigger_objs else None
                return VeilLore(**data)
                
            return VeilEntity(**data)

        except Exception as e:
            # print(f"⚠️ Mapping Warning: {e}")
            return None

    async def close(self):
        await self.client.aclose()
