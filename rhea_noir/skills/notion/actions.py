"""
Notion Skill - Interact with Notion pages and databases.
"""

import os
from typing import Dict, List, Any
from ..base import Skill


class NotionSkill(Skill):
    """
    Interact with Notion API (pages, databases, blocks).
    """
    
    name = "notion"
    description = "Interact with Notion pages and databases"
    version = "1.0.0"
    
    def __init__(self):
        super().__init__()
        self._client = None
    
    @property
    def actions(self) -> List[str]:
        return ["me", "search", "list_users", "add_media"]
    
    def _lazy_load(self):
        if self._client is None:
            try:
                from notion_client import Client
                token = os.getenv("NOTION_TOKEN")
                if token:
                    self._client = Client(auth=token)
            except ImportError:
                pass
    
    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        self._lazy_load()
        
        if not self._client:
            return self._error("Notion client not available (check NOTION_TOKEN)")
        
        try:
            if action == "me":
                user = self._client.users.me()
                return self._success(user)
            
            elif action == "list_users":
                users = self._client.users.list()
                return self._success(users)
            
            elif action == "search":
                # Search for pages/databases the integration has access to
                query = kwargs.get("query", "")
                params = {"query": query} if query else {}
                results = self._client.search(**params)
                return self._success(results)

            elif action == "add_media":
                # Add item to Entertainment Tracker
                db_id = os.getenv("NOTION_DB_ID")
                if not db_id:
                    return self._error("NOTION_DB_ID not set in .env")

                data = kwargs.get("data", {})
                title = data.get("title", "Untitled")
                
                # Map properties to specific schema
                properties = {
                    "Title": {"title": [{"text": {"content": title}}]},
                    "Status": {"select": {"name": "Want to Watch"}}, # Default status
                    "Priority": {"select": {"name": "Medium"}}, # Default
                }
                
                # Check if we have pre-formatted Notion data (e.g. from TVmaze)
                notion_data = data.get("notion_data")
                if notion_data:
                    # Merge structured data
                    if notion_data.get("Media Type"):
                        properties["Media Type"] = {"select": {"name": notion_data.get("Media Type")}}
                    if notion_data.get("Status"):
                        properties["Status"] = {"select": {"name": notion_data.get("Status")}}
                    if notion_data.get("IMDb Rating"):
                        properties["IMDb Rating"] = {"number": float(notion_data.get("IMDb Rating"))}
                    if notion_data.get("Release Date"):
                        properties["Release Date"] = {"date": {"start": notion_data.get("Release Date")}}
                    if notion_data.get("Studio"):
                        properties["Studio"] = {"rich_text": [{"text": {"content": notion_data.get("Studio") or ""}}]}
                    
                    # Multi-selects
                    if notion_data.get("Genre"):
                        genres = [{"name": g} for g in notion_data.get("Genre")]
                        properties["Genre"] = {"multi_select": genres}

                else:
                    # Fallback / Original logic for raw data (fmovies)
                    # Media Type
                    m_type = data.get("type")
                    if m_type:
                        # fmovies uses "Movie" / "TV"
                        select_name = "Movie" if "movie" in m_type.lower() else "TV Show"
                        properties["Media Type"] = {"select": {"name": select_name}}

                    # IMDb
                    imdb = data.get("imdb")
                    if imdb:
                        try:
                            # Clean string " 8.9" -> 8.9
                            val = float(str(imdb).strip())
                            properties["IMDb Rating"] = {"number": val}
                        except:
                            pass

                    # Year / Date (simple year fallback)
                    year = data.get("year")
                    if year and str(year).isdigit() and len(str(year)) == 4:
                        properties["Release Date"] = {"date": {"start": f"{year}-01-01"}}

                # Common fields
                # Poster URL
                cover = data.get("cover")
                if cover and cover.startswith("http"):
                    properties["Poster URL"] = {"url": cover}

                # Link
                link = data.get("link")
                if link and link.startswith("http"):
                    properties["Where to Watch URL"] = {"url": link}
                
                # Official Site override if available
                if data.get("official_site"):
                    properties["Where to Watch URL"] = {"url": data.get("official_site")}

                # Summary -> Notes or Description?
                summary = data.get("summary")
                if summary:
                     # Create blocks for summary since it can be long
                     pass # Currently we only set properties, but could append blocks later

                # Create page
                new_page = self._client.pages.create(
                    parent={"database_id": db_id},
                    properties=properties,
                    icon={"emoji": "🎬"}
                )
                return self._success(new_page)
            
            else:
                return self._action_not_found(action)
                
        except Exception as e:
            return self._error(f"Notion API error: {str(e)}")


skill = NotionSkill()
