from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class HindsightNote(BaseModel):
    """
    Structured memory of a completed task or significant event.
    Inspired by Confucius Agent's 'Hindsight Note' concept.
    """
    id: str = Field(description="Unique UUID for this note")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Context
    task_name: str = Field(description="Name of the task being performed")
    trigger_event: str = Field(description="What triggered this note? (e.g., 'Task Failure', 'Task Success', 'User Correction')")
    
    # core insights
    what_happened: str = Field(description="Brief summary of the execution")
    outcome: Literal["success", "failure", "partial"] = Field(description="Result of the task")
    
    # The 'Hindsight' - Critical for learning
    root_cause: Optional[str] = Field(None, description="Why did it fail? (or succeed unexpectedly)")
    key_lesson: str = Field(description="One sentence abstract rule/fact learned from this.")
    
    # For Retrieval
    tags: List[str] = Field(default_factory=list, description="Keywords for indexing")
    related_files: List[str] = Field(default_factory=list, description="Files touched during this event")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123-abc",
                "task_name": "API Integration",
                "trigger_event": "Task Failure",
                "what_happened": "Attempted to use notion_client.Client in async context.",
                "outcome": "failure",
                "root_cause": "notion_client.Client is synchronous. Must use notion_client.AsyncClient.",
                "key_lesson": "Always use AsyncClient for Notion integration in async codebases.",
                "tags": ["notion", "async", "api"],
                "related_files": ["services/notion.py"]
            }
        }
