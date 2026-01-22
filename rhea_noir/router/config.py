"""
Router Configuration Module.

Defines model tiers and the skill catalog used for routing decisions.
"""

# Model tiers - complex tasks get Pro, simple tasks get Flash
MODEL_TIERS = {
    "pro": {
        "model": "gemini-3-pro-preview",
        "thinking_level": "high",
        "skills": ["deepresearch", "computeruse", "filesearch", "stitch"],
    },
    "flash": {
        "model": "gemini-3-flash-preview",
        "thinking_level": "low",
        "skills": [],  # Everything else defaults to Flash
    },
}

# Skill catalog with descriptions for routing
SKILL_CATALOG = {
    # Research & Files (Specific)
    "deepresearch": {
        "triggers": [
            "research",
            "deep dive",
            "investigate",
            "comprehensive report",
            "analyze topic",
        ],
        "description": "Multi-step autonomous research agent",
    },
    "filesearch": {
        "triggers": [
            "search my files",
            "find in documents",
            "rag",
            "knowledge base",
            "file store",
        ],
        "description": "Semantic file search (RAG)",
    },
    # Web & Search (Generic)
    "googlesearch": {
        "triggers": [
            "search",
            "find",
            "look up",
            "what is",
            "who is",
            "latest news",
            "current",
        ],
        "description": "Real-time web search with citations",
    },
    "urlcontext": {
        "triggers": [
            "analyze url",
            "compare websites",
            "read page",
            "summarize website",
            "extract from url",
        ],
        "description": "Analyze and compare web pages",
    },
    # Location
    "googlemaps": {
        "triggers": [
            "near me",
            "restaurants",
            "directions",
            "places",
            "location",
            "find nearby",
        ],
        "description": "Location-aware search and recommendations",
    },
    # Media Creation
    "stitch": {
        "triggers": [
            "generate image",
            "create ui",
            "design",
            "make logo",
            "infographic",
            "mockup",
        ],
        "description": "UI and image generation",
    },
    "lyria": {
        "triggers": ["generate music", "create song", "compose", "make beats", "music"],
        "description": "AI music generation",
    },
    "tts": {
        "triggers": [
            "speak",
            "text to speech",
            "read aloud",
            "voice",
            "say this",
            "narrate",
        ],
        "description": "Text-to-speech generation",
    },
    # Media Understanding
    "audio": {
        "triggers": [
            "transcribe",
            "audio",
            "listen to",
            "what does this say",
            "speech to text",
        ],
        "description": "Audio understanding and transcription",
    },
    "documents": {
        "triggers": [
            "pdf",
            "document",
            "summarize file",
            "extract from pdf",
            "analyze report",
        ],
        "description": "PDF and document processing",
    },
    "youtube": {
        "triggers": ["youtube", "video summary", "watch", "youtube video"],
        "description": "YouTube video understanding",
    },
    # Downloads
    "ytdlp": {
        "triggers": [
            "download video",
            "download audio",
            "get video",
            "save video",
            "rip",
        ],
        "description": "Video/audio downloading",
    },
    "gallerydl": {
        "triggers": ["download images", "gallery", "download photos", "save images"],
        "description": "Image gallery downloading",
    },
    "coursera": {
        "triggers": ["coursera", "download course", "online course"],
        "description": "Coursera course downloading",
    },
    # RAG & Memory
    "filesearch": {
        "triggers": [
            "search my files",
            "find in documents",
            "rag",
            "knowledge base",
            "file store",
        ],
        "description": "Semantic file search (RAG)",
    },
    "memory": {
        "triggers": ["remember", "recall", "what did i say", "memory", "store this"],
        "description": "Memory and recall",
    },
    # Automation
    "computeruse": {
        "triggers": [
            "browser",
            "click",
            "automate",
            "web automation",
            "fill form",
            "navigate to",
        ],
        "description": "Browser automation",
    },
    # Entertainment
    "movies": {
        "triggers": ["movie", "film", "watch list", "recommend movie", "what to watch"],
        "description": "Movie recommendations",
    },
    "tmdb": {
        "triggers": ["tmdb", "movie database", "film info", "cast", "actor"],
        "description": "Movie database queries",
    },
    "tvmaze": {
        "triggers": ["tv show", "series", "episodes", "when does", "air date"],
        "description": "TV show information",
    },
    # Productivity
    "notion": {
        "triggers": ["notion", "notes", "database", "page", "workspace"],
        "description": "Notion integration",
    },
    "task": {
        "triggers": ["todo", "task", "reminder", "schedule", "plan"],
        "description": "Task management",
    },
    # Development
    "flutter": {
        "skill": "flutter_vibe",  # Use flutter_vibe skill
        "triggers": [
            "flutter",
            "dart",
            "create app",
            "mobile app",
            "generate widget",
            "vibe code",
            "scaffold app",
            "generate screen",
            "generate feature",
            "flutter review",
            "explain dart",
            "riverpod",
            "go_router",
        ],
        "description": "Vibe-Coded Flutter development (Riverpod, GoRouter, Material 3)",
    },
}
