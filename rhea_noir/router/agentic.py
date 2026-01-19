"""
Agentic Router Module.
Implements the deep thought routing strategy using Gemini 3 Pro for complex ambiguity.
"""
from typing import Dict, Any, Optional
import json
from rhea_noir.router.base import BaseRouter
from rhea_noir.router.config import SKILL_CATALOG, MODEL_TIERS


class AgenticStrategy(BaseRouter):
    """
    Agentic routing strategy.
    Uses Gemini 3 Pro (High Thinking) to resolve ambiguous or complex queries.
    Equivalent to LLMRouter's MultiRound or Agentic Router concepts.
    """

    def route(self, request: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Route using deep reasoning."""
        return self._pro_route(request)

    def _pro_route(self, request: str) -> Dict[str, Any]:
        """Use Gemini 3 Pro for high-reasoning routing."""
        try:
            # pylint: disable=import-outside-toplevel
            from google.genai import types

            skill_list = self._get_skill_list_text()

            prompt = f"""You are Rhea's Senior Command Router.
The fast router failed to confidently classify this request.
Analyze the user request deeply and determine the best skill.

Available skills:
{skill_list}

User request: "{request}"

Respond with JSON only:
{{"skill": "skill_name", "action": "action_name", "params": {{}}, "reason": "detailed reasoning"}}

If no skill matches, use: {{"skill": null, "reason": "explanation"}}"""

            # Use Gemini 3 Pro with high thinking
            response = self.client.models.generate_content(
                model=MODEL_TIERS["pro"]["model"],
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    thinking_config=types.ThinkingConfig(
                        thinking_level=MODEL_TIERS["pro"]["thinking_level"]
                    )
                )
            )

            result = json.loads(response.text)
            result["confidence"] = 0.95  # Pro is authoritative
            result["method"] = "gemini-pro-agentic"
            
            # Determine tier
            result["tier"] = self._determine_tier(result.get("skill"))

            return result

        except Exception as e:
            return {"skill": None, "error": str(e), "method": "failed"}
