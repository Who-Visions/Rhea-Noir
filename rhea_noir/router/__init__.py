"""
Rhea Router Package.
Exposes the main Reflex router and capabilities.
"""
from typing import Dict, Any, List, Optional
from rhea_noir.router.fast import FastStrategy
from rhea_noir.router.agentic import AgenticStrategy
from rhea_noir.router.config import SKILL_CATALOG


class Reflex:
    """
    Rhea's intelligent skill router (Singleton).
    Orchestrates routing between Fast (Flash) and Agentic (Pro) strategies.
    """

    def __init__(self):
        self._fast_router = FastStrategy()
        self._agentic_router = AgenticStrategy()
        self._registry = None

    def _get_registry(self):
        if self._registry is None:
            # pylint: disable=import-outside-toplevel
            from rhea_noir.skills import registry

            self._registry = registry
        return self._registry

    def route(self, request: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Route a natural language request to the appropriate skill.

        Algorithm:
        1. Try FastStrategy (Keyword + Flash)
        2. If confidence < 0.7, try AgenticStrategy (Pro)
        """
        # 1. Fast Route
        result = self._fast_router.route(request, context)

        # 2. Check confidence (fallback to Pro if needed)
        confidence = result.get("confidence", 0.0)
        # Only fallback if it wasn't a keyword match (which is usually high confidence)
        # and if confidence is low.
        if confidence < 0.6 and result.get("method") != "keyword":
            # Fallback to Agentic
            pro_result = self._agentic_router.route(request, context)
            if pro_result.get("confidence", 0.0) > confidence:
                return pro_result

        return result

    def execute(self, request: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Route and execute a request in one call.
        """
        # Route the request
        route_result = self.route(request, context)

        if not route_result.get("skill"):
            return {
                "success": False,
                "error": "No matching skill found",
                "routing": route_result,
            }

        skill_name = route_result["skill"]
        action = route_result.get("action", "default")
        params = route_result.get("params", {})

        # Get the skill
        registry = self._get_registry()
        skill = registry.get(skill_name)

        if not skill:
            return {
                "success": False,
                "error": f"Skill '{skill_name}' not found in registry",
                "routing": route_result,
            }

        # Execute the skill action
        try:
            # If skill has the action method, call it
            if hasattr(skill, action):
                method = getattr(skill, action)
                result = method(**params) if params else method(request)
            elif hasattr(skill, "execute"):
                result = skill.execute(action, **params)
            else:
                # Fall back to calling first available method
                result = {"error": f"Action '{action}' not found on skill"}

            return {
                "success": True,
                "skill": skill_name,
                "action": action,
                "result": result,
                "routing": route_result,
            }
        except Exception as e:
            return {
                "success": False,
                "skill": skill_name,
                "error": str(e),
                "routing": route_result,
            }

    def list_capabilities(self) -> List[Dict]:
        """List all available skills and their triggers."""
        return [
            {
                "skill": name,
                "description": info["description"],
                "triggers": info["triggers"],
            }
            for name, info in SKILL_CATALOG.items()
        ]


# Singleton instance
reflex = Reflex()


# Convenience functions for import compatibility
def route(request: str) -> Dict:
    """Route a request."""
    return reflex.route(request)


def execute(request: str) -> Dict:
    """Route and execute a request."""
    return reflex.execute(request)


def capabilities() -> List[Dict]:
    """List capabilities."""
    return reflex.list_capabilities()
