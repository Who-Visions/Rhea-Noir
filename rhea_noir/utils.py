"""
Rhea Noir Utilities - Common helper functions
"""

from datetime import datetime, timezone, timedelta

# Use zoneinfo (Python 3.9+) for accurate Eastern Time
try:
    from zoneinfo import ZoneInfo
    EASTERN = ZoneInfo("America/New_York")
except ImportError:
    # Fallback for older Python - use fixed offset
    EASTERN = timezone(timedelta(hours=-5))  # EST (winter)


def get_eastern_time() -> datetime:
    """Get current time in Eastern Time zone (America/New_York)"""
    return datetime.now(EASTERN)


def get_eastern_timestamp() -> str:
    """Get current Eastern time as ISO format string"""
    return get_eastern_time().isoformat()


def get_eastern_display() -> str:
    """Get current Eastern time in readable format: 2025-12-09 05:22:42 ET"""
    return get_eastern_time().strftime("%Y-%m-%d %H:%M:%S ET")


def get_eastern_time_short() -> str:
    """Get current Eastern time as HH:MM:SS"""
    return get_eastern_time().strftime("%H:%M:%S")


# Convenient aliases
now = get_eastern_time
timestamp = get_eastern_timestamp
