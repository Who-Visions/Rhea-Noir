"""
Base Router Module.
Defines the abstract base class for all routing strategies.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseRouter(ABC):
    """
    Abstract base class for routing strategies.
    Mimics LLMRouter's MetaRouter pattern.
    """

    def __init__(self, client=None):
        self._client = client

    @property
    def client(self):
        """Lazy load Gemini client."""
        if self._client is None:
            # pylint: disable=import-outside-toplevel
            from google import genai

            self._client = genai.Client()
        return self._client

    @abstractmethod
    def route(self, request: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Route a request to a skill.

        Args:
            request: The user's natural language request.
            context: Optional context (location, files, etc).

        Returns:
            Dict containing routing decision (skill, action, params, etc).
        """

    def _get_skill_list_text(self) -> str:
        """Generate formatted skill list for prompts."""
        # pylint: disable=import-outside-toplevel
        from rhea_noir.router.config import SKILL_CATALOG

        return "\n".join([
            f"- {name}: {info['description']}"
            for name, info in SKILL_CATALOG.items()
        ])

    def _determine_tier(self, skill: str) -> str:
        """Determine if skill is pro or flash tier."""
        # pylint: disable=import-outside-toplevel
        from rhea_noir.router.config import MODEL_TIERS
        
        if skill and skill in MODEL_TIERS["pro"]["skills"]:
            return "pro"
        return "flash"
