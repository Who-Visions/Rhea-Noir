from typing import Dict, Any, List
from rhea_noir.skills.base import Skill
from services.memory import LoreMemoryService
from rhea_noir.memory.models import HindsightNote
import uuid
import json

class MemorySkill(Skill):
    """
    Skill for Active Memory Management (Confucius Style).
    Allows Rhea to create 'Hindsight Notes' and manage her own long-term context.
    """
    
    def __init__(self):
        super().__init__()
        self.memory = LoreMemoryService()

    @property
    def name(self) -> str:
        return "memory"

    @property
    def description(self) -> str:
        return "Tools for self-reflection, creating hindsight notes, and retrieving experiences."

    @property
    def actions(self) -> List[str]:
        return ["reflect", "recall_notes"]

    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Executes memory actions.
        NOTE: This is a synchronous wrapper around async DB calls.
        """
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        if action == "reflect":
            return loop.run_until_complete(self._reflect(**kwargs))
        elif action == "recall_notes":
            return loop.run_until_complete(self._recall_notes(**kwargs))
        else:
            return {"error": f"Unknown action: {action}"}

    async def _reflect(self, 
                      task_name: str, 
                      outcome: str, 
                      what_happened: str, 
                      key_lesson: str,
                      trigger_event: str = "Self-Reflection",
                      root_cause: str = None,
                      tags: List[str] = []) -> Dict[str, Any]:
        """
        Creates a new Hindsight Note.
        """
        note = HindsightNote(
            id=str(uuid.uuid4()),
            task_name=task_name,
            trigger_event=trigger_event,
            what_happened=what_happened,
            outcome=outcome,
            root_cause=root_cause,
            key_lesson=key_lesson,
            tags=tags
        )
        
        await self.memory.initialize()
        # Ensure timestamp is serialized to string
        note_data = json.loads(note.json()) 
        await self.memory.add_hindsight_note(note_data)
        
        return {
            "status": "success", 
            "message": f"Hindsight note recorded: {key_lesson}",
            "note_id": note.id
        }

    async def _recall_notes(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """
        Searches past Hindsight Notes.
        """
        await self.memory.initialize()
        notes = await self.memory.search_notes(query, limit)
        return {"notes": notes, "count": len(notes)}


skill = MemorySkill()
