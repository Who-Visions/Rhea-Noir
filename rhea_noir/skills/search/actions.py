"""
Search Skill - Unified search across multiple sources.
"""

from typing import Dict, List, Any
from ..base import Skill


class SearchSkill(Skill):
    """
    Search across knowledge bases, web, and memory.
    """
    
    name = "search"
    description = "Search knowledge bases, web, and memory"
    version = "1.0.0"
    
    def __init__(self):
        super().__init__()
        self._searcher = None
    
    @property
    def actions(self) -> List[str]:
        return ["web", "knowledge", "memory", "unified"]
    
    def _lazy_load(self):
        if self._searcher is None:
            try:
                from rhea_noir.search import RheaSearch
                self._searcher = RheaSearch()
            except ImportError:
                pass
    
    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        self._lazy_load()
        
        if not self._searcher:
            return self._error("Search system not available")
        
        query = kwargs.get("query", "")
        if not query:
            return self._error("Query is required")
        
        if action == "web":
            result = self._searcher.search_with_grounding(query)
            return self._success(result)
        elif action == "knowledge":
            results = self._searcher.search_knowledge(query)
            return self._success({"results": results})
        elif action == "memory":
            results = self._searcher.search_memory(query)
            return self._success({"results": results})
        elif action == "unified":
            sources = kwargs.get("sources", ["memory", "knowledge", "web"])
            results = self._searcher.unified_search(query, sources)
            return self._success(results)
        else:
            return self._action_not_found(action)


skill = SearchSkill()
