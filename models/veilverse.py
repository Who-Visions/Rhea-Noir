from enum import Enum
from typing import List, Optional, Any
from pydantic import BaseModel, Field

class VeilVerseCategory(str, Enum):
    EVENT = "Event"
    LORE = "Lore"
    CHARACTER = "Character"
    ORGANIZATION = "Organization"
    LOCATION = "Location"

class UniverseEra(str, Enum):
    PRE_COLLAPSE = "Pre Collapse Era"
    COLLAPSE = "Collapse Era"
    RECONSTRUCTION = "Reconstruction Era"
    NEON_FUTURE = "Near Future Era"
    FAR_FUTURE = "Far Future Era"
    DEEP_TIME = "Deep Time Era"

class RenderStatus(str, Enum):
    NOT_STARTED = "Not Started"
    BRIEFING = "Briefing"     # Equiv to Concept/Idea
    PROMPTING = "Prompting"
    RENDERING = "Rendering"
    POLISHING = "Polishing"
    APPROVED = "Approved"
    ARCHIVED = "Archived"

class VeilEntity(BaseModel):
    """
    Represents a core entity in the VeilVerse Universe Database.
    Mapped from Notion Database: 'VeilVerse Universe Best'
    """
    notion_id: Optional[str] = Field(None, description="The Notion Page ID")
    name: str = Field(..., description="The Title/Name of the entity")
    description: Optional[str] = Field(None, description="Short textual description or flavor text")
    
    # Core Logic
    category: Optional[VeilVerseCategory] = None
    universe_era: Optional[UniverseEra] = None
    
    # Visuals
    icon: Optional[str] = Field(None, description="Page Dictionary Icon (Emoji or URL)")
    render_status: Optional[RenderStatus] = None
    image_url: Optional[str] = Field(None, description="The 'Asset Folder' or 'Image' property link")
    color_palette: Optional[List[str]] = Field(default_factory=list)
    
    # Lore
    canon_confidence: Optional[float] = Field(None, ge=0, le=100)
    canon_status: Optional[str] = None # e.g. "Canon Locked", "Soft Canon"
    
    # Metadata
    url: Optional[str] = None
    slug: Optional[str] = None

class VeilEvent(VeilEntity):
    """Specialized entity for Events (Nightlife, Cons)"""
    event_date: Optional[str] = None # ISO Date or simple string for now
    location: Optional[str] = None
    price: Optional[str] = None
    ticket_link: Optional[str] = None

class VeilLore(VeilEntity):
    """Specialized entity for World Rules, Characters, etc."""
    power_level: Optional[str] = None
    species: Optional[List[str]] = None
    veil_activation_trigger: Optional[str] = None
