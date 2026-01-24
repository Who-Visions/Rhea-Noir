from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
import asyncio

# --- Data Models ---

class RSVPStatus(str, Enum):
    GOING = "going"
    MAYBE = "maybe"
    NOT_GOING = "not_going"

class UserRole(str, Enum):
    ATTENDEE = "attendee"
    COSPLAYER = "cosplayer"
    PHOTOGRAPHER = "photographer"
    STAFF = "staff"
    SECURITY = "security"

class ConsentLevel(str, Enum):
    YES = "yes"
    ASK_FIRST = "ask_first"
    NO = "no"

class BlerdconEvent(BaseModel):
    id: str = "blerdcon_2026_cars"
    name: str = "On Top of Cars"
    verified: bool = True
    dates: str = "March 6-8, 2026"
    venue: str = "Hyatt Regency Crystal City & Hilton Crystal City"
    location_slot: str = "TBD (Garage Top or Main Plaza)"
    theme: str = "Carz and Barz"
    visual_tags: List[str] = ["Panty and Stocking", "Afro Samurai", "Blue Lock"]
    status: str = "scheduled"

class ConsentProfile(BaseModel):
    user_id: str
    photo_consent: ConsentLevel = ConsentLevel.ASK_FIRST
    posting_consent: bool = False # Approve first
    social_handles: Dict[str, str] = {} # e.g. {"instagram": "@..."}
    boundaries: Optional[str] = "Family friendly only"
    badge_color: str = "yellow" # Derived from consent (green/yellow/red)

class BlerdconRSVP(BaseModel):
    user_id: str
    status: RSVPStatus
    role: UserRole = UserRole.ATTENDEE
    guests: int = 0
    timestamp: datetime = Field(default_factory=datetime.now)

class Announcement(BaseModel):
    id: str
    title: str
    message: str
    type: str = "info" # info, alert, emergency
    timestamp: datetime = Field(default_factory=datetime.now)

# --- Service ---

class BlerdconService:
    def __init__(self):
        # In-Memory Storage for MVP
        self._event = BlerdconEvent()
        self._rsvps: Dict[str, BlerdconRSVP] = {}
        self._consent_profiles: Dict[str, ConsentProfile] = {}
        self._announcements: List[Announcement] = [
            Announcement(
                id="1", 
                title="Protocol Initialized", 
                message="Rhea Noir is now monitoring Blerdcon Ops.",
                type="info"
            )
        ]

    async def get_event(self) -> BlerdconEvent:
        return self._event

    async def update_rsvp(self, rsvp: BlerdconRSVP) -> BlerdconRSVP:
        self._rsvps[rsvp.user_id] = rsvp
        return rsvp

    async def get_rsvp(self, user_id: str) -> Optional[BlerdconRSVP]:
        return self._rsvps.get(user_id)

    async def update_consent(self, profile: ConsentProfile) -> ConsentProfile:
        # Auto-derive badge color
        if profile.photo_consent == ConsentLevel.YES:
            profile.badge_color = "green"
        elif profile.photo_consent == ConsentLevel.NO:
            profile.badge_color = "red"
        else:
            profile.badge_color = "yellow"
            
        self._consent_profiles[profile.user_id] = profile
        return profile

    async def get_consent(self, user_id: str) -> Optional[ConsentProfile]:
        return self._consent_profiles.get(user_id)

    async def get_feed(self) -> List[Announcement]:
        return sorted(self._announcements, key=lambda x: x.timestamp, reverse=True)

    async def post_announcement(self, announcement: Announcement):
        self._announcements.insert(0, announcement)
        return announcement

    async def get_stats(self) -> Dict[str, Any]:
        return {
            "total_rsvps": len(self._rsvps),
            "going": sum(1 for r in self._rsvps.values() if r.status == RSVPStatus.GOING),
            "cosplayers": sum(1 for r in self._rsvps.values() if r.role == UserRole.COSPLAYER),
            "photographers": sum(1 for r in self._rsvps.values() if r.role == UserRole.PHOTOGRAPHER)
        }
