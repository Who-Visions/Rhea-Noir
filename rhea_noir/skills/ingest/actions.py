"""
Ingest Skill - Global knowledge ingestion tool for Rhea Noir.
Centralizes URL and text ingestion with memory-aware verification.
"""

import asyncio
from typing import Dict, List, Any, Optional
from ..base import Skill


class IngestSkill(Skill):
    """
    Consolidated ingestion skill for YouTube, Web, and Text.
    Uses IngestorService for LLM parsing and LoreMemoryService for verification.
    """

    name = "ingest"
    description = "Ingest YouTube, Web, and Text intelligence into Rhea's memory"
    version = "1.0.0"

    def __init__(self):
        super().__init__()
        self._ingestor = None
        self._memory = None

    @property
    def actions(self) -> List[str]:
        return ["ingest", "verify"]

    def _lazy_load(self):
        """Load services only when needed."""
        if self._ingestor is None:
            try:
                from services.ingestor import IngestorService
                self._ingestor = IngestorService()
            except ImportError:
                pass

        if self._memory is None:
            try:
                from services.memory import LoreMemoryService
                self._memory = LoreMemoryService()
            except ImportError:
                pass

    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        self._lazy_load()

        if action == "verify":
            return asyncio.run(self._verify(kwargs.get("query", "")))

        elif action == "ingest":
            return asyncio.run(self._ingest(**kwargs))

        else:
            return self._action_not_found(action)

    async def _verify(self, query: str) -> Dict[str, Any]:
        if not self._memory:
            return self._error("Memory service not available")

        if not query:
            return self._error("Query is required for verification")

        await self._memory.initialize()
        results = await self._memory.search_lore(query)

        exists = len(results) > 0
        return self._success({
            "exists": exists,
            "match_count": len(results),
            "matches": results[:3]
        })

    async def _ingest(self, **kwargs) -> Dict[str, Any]:
        if not self._ingestor:
            return self._error("Ingestor service not available")

        url = kwargs.get("url", "")
        content = kwargs.get("content", "")
        hint = kwargs.get("hint", "")
        dry_run = kwargs.get("dry_run", False)

        if not url and not content:
            return self._error("Either url or content is required")

        # 1. Performance memory check (recursive check)
        check_query = url if url else content[:100]
        verification = await self._verify(check_query)
        if verification["success"] and verification["result"]["exists"]:
            return self._error(f"Intelligence already exists in memory: {verification['result']['matches'][0]['name']}")

        # 2. Proceed with ingestion
        input_data = url if url else content

        # Note: IngestorService.ingest_transcript handles both URL and Text
        success = await self._ingestor.ingest_transcript(input_data, hint)

        if success:
            return self._success("Intelligence successfully integrated into Rhea's memory.")
        else:
            return self._error("Ingestion process failed. Check server logs.")


skill = IngestSkill()
