"""
YouTube Skill - Ingest video transcripts.
"""

from typing import Dict, List, Any
from ..base import Skill


class YouTubeSkill(Skill):
    """
    Ingest YouTube video transcripts into memory.
    """
    
    name = "youtube"
    description = "Ingest YouTube video transcripts"
    version = "1.0.0"
    
    def __init__(self):
        super().__init__()
        self._ingestor = None
    
    @property
    def actions(self) -> List[str]:
        return ["ingest", "info"]
    
    def _lazy_load(self):
        if self._ingestor is None:
            try:
                from rhea_noir.youtube import YouTubeIngestor
                self._ingestor = YouTubeIngestor()
            except ImportError:
                pass
    
    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        self._lazy_load()
        
        if not self._ingestor:
            return self._error("YouTube ingestor not available")
        
        url = kwargs.get("url", "")
        if not url:
            return self._error("URL is required")
        
        if action == "info":
            video_id = self._ingestor.extract_video_id(url)
            if not video_id:
                return self._error("Invalid YouTube URL")
            info = self._ingestor.get_video_info(video_id)
            return self._success(info) if info else self._error("Could not fetch info")
        
        elif action == "ingest":
            result = self._ingestor.ingest_video(
                url,
                source=kwargs.get("source", "YouTube"),
                categories=kwargs.get("categories"),
                dry_run=kwargs.get("dry_run", False),
            )
            return self._success(result) if result else self._error("Ingestion failed")
        
        else:
            return self._action_not_found(action)


skill = YouTubeSkill()
