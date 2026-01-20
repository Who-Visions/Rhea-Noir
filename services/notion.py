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
            
        payload = {"page_size": limit}
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
            
            # Simple chunking to avoid 2000 char limit error
            chunks = [content[i:i+2000] for i in range(0, len(content), 2000)]
            
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
