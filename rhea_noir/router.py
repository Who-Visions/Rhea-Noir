"""
Rhea Noir Model Router - Intelligent model tier selection
Routes to appropriate model based on task complexity
"""

import re
from typing import Optional, Tuple
from enum import Enum


class ModelTier(Enum):
    """Model tiers from cheapest to most powerful"""
    LITE = "lite"
    STANDARD = "standard"
    PRO = "pro"
    ELITE = "elite"
    IMAGE = "image"              # Fallback image model
    ELITE_IMAGE = "elite_image"  # Primary image model (preferred)


class ModelRouter:
    """Intelligent routing to appropriate Gemini model tier"""

    # Model configurations
    MODELS = {
        ModelTier.LITE: {
            "name": "gemini-2.5-flash-lite",
            "location": "us-central1",
            "description": "Fast, cheap - simple queries",
        },
        ModelTier.STANDARD: {
            "name": "gemini-2.5-flash",
            "location": "us-central1",
            "description": "Balanced - default conversations",
        },
        ModelTier.PRO: {
            "name": "gemini-2.5-pro",
            "location": "us-central1",
            "description": "Reasoning - complex tasks",
        },
        ModelTier.ELITE: {
            "name": "gemini-3-pro-preview",
            "location": "global",  # MUST be global endpoint
            "description": "Advanced - research, elite tasks",
        },
        ModelTier.ELITE_IMAGE: {
            "name": "gemini-3-pro-image-preview",
            "location": "global",  # MUST be global endpoint
            "description": "Elite multimodal - primary image model",
        },
        ModelTier.IMAGE: {
            "name": "gemini-2.5-flash-image",
            "location": "us-central1",
            "description": "Fallback multimodal - image understanding",
        },
    }

    # Patterns that suggest higher complexity
    COMPLEXITY_PATTERNS = {
        ModelTier.ELITE: [
            r'\bresearch\b', r'\banalyze\b.*\b(deeply|thoroughly)\b',
            r'\bcomplex\b.*\b(architecture|system)\b',
            r'\boptimize\b.*\bperformance\b',
            r'\bdesign\b.*\b(pattern|system)\b',
        ],
        ModelTier.PRO: [
            r'\bdebug\b', r'\brefactor\b', r'\barchitecture\b',
            r'\bexplain\b.*\b(why|how)\b', r'\bcompare\b',
            r'\bimplement\b.*\b(feature|system)\b',
            r'\breview\b.*\bcode\b', r'\btest\b.*\bstrategy\b',
        ],
        ModelTier.STANDARD: [
            r'\bwrite\b', r'\bcreate\b', r'\bgenerate\b',
            r'\bhelp\b.*\bwith\b', r'\bhow\b.*\bto\b',
            r'\bwhat\b.*\bis\b', r'\bcan\b.*\byou\b',
        ],
        ModelTier.LITE: [
            r'^(hi|hello|hey|thanks|ok|yes|no)\b',
            r'\?$',  # Simple questions
            r'^.{1,50}$',  # Very short inputs
        ],
    }

    # Keywords that suggest image involvement
    IMAGE_KEYWORDS = [
        'image', 'picture', 'photo', 'screenshot', 'diagram',
        'visual', 'see', 'look at', 'show me', 'render',
    ]

    def __init__(self, default_tier: ModelTier = ModelTier.STANDARD):
        """Initialize router with default tier"""
        self.default_tier = default_tier
        self.override_tier: Optional[ModelTier] = None

    def route(self, query: str, has_image: bool = False) -> Tuple[str, str, ModelTier]:
        """
        Route query to appropriate model.

        Returns:
            Tuple of (model_name, location, tier)
        """
        # Check for manual override
        if self.override_tier:
            tier = self.override_tier
            self.override_tier = None  # Reset after use
        # Check for image content - use elite image model (global) as primary
        elif has_image or self._has_image_keywords(query):
            tier = ModelTier.ELITE_IMAGE  # gemini-3-pro-image-preview (global)
        else:
            tier = self._analyze_complexity(query)

        config = self.MODELS[tier]
        return config["name"], config["location"], tier

    def _has_image_keywords(self, query: str) -> bool:
        """Check if query mentions images"""
        query_lower = query.lower()
        return any(kw in query_lower for kw in self.IMAGE_KEYWORDS)

    def _analyze_complexity(self, query: str) -> ModelTier:
        """Analyze query to determine complexity tier"""
        query_lower = query.lower()

        # Check patterns from most complex to least
        for tier in [ModelTier.ELITE, ModelTier.PRO, ModelTier.STANDARD, ModelTier.LITE]:
            patterns = self.COMPLEXITY_PATTERNS.get(tier, [])
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return tier

        return self.default_tier

    def set_override(self, tier: ModelTier):
        """Manually override next routing decision"""
        self.override_tier = tier

    def get_model_info(self, tier: ModelTier) -> dict:
        """Get full info for a model tier"""
        return self.MODELS[tier]

    @classmethod
    def list_models(cls) -> list:
        """List all available models"""
        return [
            {
                "tier": tier.value,
                "name": config["name"],
                "location": config["location"],
                "description": config["description"],
            }
            for tier, config in cls.MODELS.items()
        ]


# Global router instance
router = ModelRouter()
