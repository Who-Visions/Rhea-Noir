"""
TVmaze Skill - Rich TV metadata and user dashboard integration.
"""

import os
import requests
from typing import Dict, List, Any
from ..base import Skill

class TvMazeSkill(Skill):
    """
    Search TVmaze and manage user library.
    """
    
    name = "tvmaze"
    description = "TVmaze metadata and user dashboard"
    version = "1.0.0"
    
    BASE_URL = "https://api.tvmaze.com"
    
    @property
    def actions(self) -> List[str]:
        return ["search", "search_people", "dashboard", "show_info"]
    
    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        api_key = os.getenv("TVMAZE_API_KEY")
        
        try:
            if action == "search":
                return self._search_shows(kwargs.get("query", ""))
            
            elif action == "search_people":
                return self._search_people(kwargs.get("query", ""))
            
            elif action == "show_info":
                # Get detailed info by ID or Single Search
                return self._get_show_info(kwargs.get("id"), kwargs.get("query"))

            elif action == "dashboard":
                if not api_key:
                    return self._error("TVMAZE_API_KEY required for dashboard")
                return self._get_dashboard(api_key)
            
            else:
                return self._action_not_found(action)
                
        except Exception as e:
            return self._error(f"TVmaze error: {e}")

    def _search_shows(self, query: str) -> Dict[str, Any]:
        if not query: return self._error("Query required")
        
        # Single search: https://api.tvmaze.com/search/shows?q=girls
        url = f"{self.BASE_URL}/search/shows"
        resp = requests.get(url, params={"q": query}, timeout=10)
        resp.raise_for_status()
        
        data = resp.json()
        results = []
        for item in data:
            show = item.get("show", {})
            results.append(self._parse_show(show))
            
        return self._success({"query": query, "results": results})

    def _search_people(self, query: str) -> Dict[str, Any]:
        if not query: return self._error("Query required")
        
        url = f"{self.BASE_URL}/search/people"
        resp = requests.get(url, params={"q": query}, timeout=10)
        resp.raise_for_status()
        return self._success(resp.json())

    def _get_show_info(self, show_id=None, query=None) -> Dict[str, Any]:
        if show_id:
            url = f"{self.BASE_URL}/shows/{show_id}"
            params = {"embed": "cast"} # Embed cast info
        elif query:
            url = f"{self.BASE_URL}/singlesearch/shows"
            params = {"q": query, "embed": "cast"}
        else:
            return self._error("ID or Query required")
            
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 404:
            return self._error("Show not found")
        resp.raise_for_status()
        
        show = resp.json()
        return self._success(self._parse_show(show, detailed=True))

    def _get_dashboard(self, api_key: str) -> Dict[str, Any]:
        # Sadly TVmaze API doesn't have a simple 'dashboard' endpoint for everything.
        # But we can check 'follows' or 'watchlist' if the API supports it.
        # Auth usually via basic auth or key.
        # User Endpoint: https://api.tvmaze.com/v1/user/follows/shows?embed=show
        # Note: Writing takes Premium usually, reading is okay.
        
        # Using the standard User API endpoint structure
        url = "https://api.tvmaze.com/v1/user/follows/shows"
        # API Key is usually passed as username/apikey in basic auth or token?
        # TVmaze docs say for basic auth: username / apikey
        # But requests usually just needs params or header. 
        # Actually for API Key access, you might just do standard requests if documented.
        # Let's try Basic Auth with 'whovisions' (from prompt) and the key.
        # Or usually it is simple: authorization header? 
        # Checking docs standard: it is often Basic Auth. 
        
        # Let's try standard Basic Auth with the key as the password, username as the email user?
        # Provided: "Your API key can be used to read from or write to your TVmaze account... basic auth with your username and this API key".
        
        # Username from prompt: "Whovisions" (or email)
        # Assuming username "Whovisions"
        
        try:
            resp = requests.get(
                url, 
                auth=("Whovisions", api_key),
                params={"embed": "show"},
                timeout=10
            )
            resp.raise_for_status()
            
            follows = []
            for item in resp.json():
                # item level usually has check info, embedded show has show info
                show = item.get("_embedded", {}).get("show", {})
                follows.append(self._parse_show(show))
                
            return self._success({"follows": follows})
        except Exception as e:
            return self._error(f"Dashboard auth failed: {e}")

    def _parse_show(self, show: Dict, detailed=False) -> Dict:
        # Extract clean data for Notion
        try:
            # Clean summary (remove HTML tags)
            summary = show.get("summary", "")
            if summary:
                summary = summary.replace("<p>", "").replace("</p>", "").replace("<b>", "").replace("</b>", "")
            
            data = {
                "title": show.get("name"),
                "year": show.get("premiered", "")[:4] if show.get("premiered") else "",
                "imdb": show.get("rating", {}).get("average"),
                "type": show.get("type", "TV Show"),
                "status": show.get("status"),
                "link": show.get("url"), # TVmaze link
                "official_site": show.get("officialSite"),
                "cover": show.get("image", {}).get("original") if show.get("image") else None,
                "summary": summary,
                "genres": show.get("genres", []),
                "network": show.get("network", {}).get("name") if show.get("network") else show.get("webChannel", {}).get("name"),
                "runtime": show.get("runtime"),
                "notion_data": { # pre-format for notion skill
                    "Media Type": "TV Show" if show.get("type") != "Movie" else "Movie", # TVmaze is mostly TV
                    "IMDb Rating": show.get("rating", {}).get("average"),
                    "Release Date": show.get("premiered"),
                    "Status": "Watching" if show.get("status") == "Running" else "Completed",
                    "Genre": show.get("genres", []),
                    "Studio": show.get("network", {}).get("name") if show.get("network") else show.get("webChannel", {}).get("name"),
                    "Creator": "", 
                    "Air Time": f"{', '.join(show.get('schedule', {}).get('days', []))} at {show.get('schedule', {}).get('time', '')}".strip(" at"),
                }
            }
            return data
        except:
            return show

skill = TvMazeSkill()
