"""
Memory Skill - Store and recall conversation memories.
"""

from typing import Dict, List, Any, Optional
from ..base import Skill


class MemorySkill(Skill):
    """
    Rhea's memory system.
    - Store messages with keywords
    - Recall by semantic search
    - Sync to cloud (BigQuery)
    """
    
    name = "memory"
    description = "Store and recall conversation memories"
    version = "1.0.0"
    
    def __init__(self):
        super().__init__()
        self._stm = None
        self._sync = None
        self._extractor = None
    
    @property
    def actions(self) -> List[str]:
        return ["store", "recall", "sync", "stats"]
    
    def _lazy_load(self):
        """Lazy load memory components."""
        if self._stm is None:
            try:
                from rhea_noir.memory import ShortTermMemory, MemorySync, KeywordExtractor
                self._stm = ShortTermMemory()
                self._extractor = KeywordExtractor()
                self._sync = MemorySync(stm=self._stm)
            except ImportError:
                pass
    
    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute a memory action."""
        self._lazy_load()
        
        if not self._stm:
            return self._error("Memory system not available")
        
        if action == "store":
            return self._store(**kwargs)
        elif action == "recall":
            return self._recall(**kwargs)
        elif action == "sync":
            return self._sync_to_cloud()
        elif action == "stats":
            return self._get_stats()
        else:
            return self._action_not_found(action)
    
    def _store(
        self,
        role: str = "user",
        content: str = "",
        keywords: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Store a message in memory."""
        if not content:
            return self._error("Content is required")
        
        # Auto-extract keywords if not provided
        if keywords is None and self._extractor:
            keywords = self._extractor.extract(content)
        
        try:
            self._stm.store(role=role, content=content, keywords=keywords or [])
            return self._success({
                "stored": True,
                "keywords": keywords or [],
            })
        except Exception as e:
            return self._error(str(e))
    
    def _recall(
        self,
        query: str = "",
        limit: int = 5,
        **kwargs
    ) -> Dict[str, Any]:
        """Search memories by query."""
        if not query:
            return self._error("Query is required")
        
        try:
            results = self._stm.recall(query, limit=limit)
            return self._success({
                "count": len(results),
                "memories": results,
            })
        except Exception as e:
            return self._error(str(e))
    
    def _sync_to_cloud(self) -> Dict[str, Any]:
        """Force sync to BigQuery."""
        if not self._sync:
            return self._error("Cloud sync not configured")
        
        try:
            count = self._sync.force_sync()
            return self._success({
                "synced": count,
            })
        except Exception as e:
            return self._error(str(e))
    
    def _get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        try:
            stats = self._stm.get_stats()
            return self._success(stats)
        except Exception as e:
            return self._error(str(e))


# Skill instance for registry
skill = MemorySkill()
