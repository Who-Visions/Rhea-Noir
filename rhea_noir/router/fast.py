"""
Fast Router Module.
Implements the fast routing strategy using keyword matching and Gemini 3 Flash.
"""
from typing import Dict, Any, Optional
import json
from rhea_noir.router.base import BaseRouter
from rhea_noir.router.config import SKILL_CATALOG, MODEL_TIERS


class FastStrategy(BaseRouter):
    """
    Fast routing strategy.
    Tries keyword matching first, then falls back to Gemini 3 Flash (Low Thinking).
    """

    def route(self, request: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Route using fast methods."""
        # 1. Keyword match
        quick_match = self._quick_match(request.lower())
        if quick_match:
            return quick_match

        # 2. Gemini 3 Flash Low Thinking
        return self._flash_route(request)

    def _quick_match(self, request: str) -> Optional[Dict]:
        """Fast keyword-based routing."""
        for skill_name, info in SKILL_CATALOG.items():
            for trigger in info["triggers"]:
                if trigger in request:
                    is_pro = skill_name in MODEL_TIERS["pro"]["skills"]
                    return {
                        "skill": skill_name,
                        "confidence": 0.8,
                        "method": "keyword",
                        "tier": "pro" if is_pro else "flash"
                    }
        return None

    def _flash_route(self, request: str) -> Dict[str, Any]:
        """Use Gemini 3 Flash for intelligent but fast routing."""
        try:
            # pylint: disable=import-outside-toplevel
            from google.genai import types

            skill_list = self._get_skill_list_text()

            prompt = f"""You are Rhea's skill router.
Given a user request, determine which skill to use.

Available skills:
{skill_list}

User request: "{request}"

Respond with JSON only:
{{"skill": "skill_name", "action": "action_name", "params": {{}}, "reason": "why"}}

If no skill matches, use: {{"skill": null, "reason": "explanation"}}"""

            # Use Gemini 3 Flash with low thinking
            response = self.client.models.generate_content(
                model=MODEL_TIERS["flash"]["model"],
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    thinking_config=types.ThinkingConfig(
                        thinking_level=MODEL_TIERS["flash"]["thinking_level"]
                    )
                )
            )

            result = json.loads(response.text)
            result["confidence"] = 0.9
            result["method"] = "gemini-flash"
            
            # Determine tier
            result["tier"] = self._determine_tier(result.get("skill"))

            return result

        except Exception as e:
            return {"skill": None, "error": str(e), "method": "failed"}
