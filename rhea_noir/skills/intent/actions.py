"""
Intent Skill - Detect user intent.
"""

from typing import Dict, List, Any
from ..base import Skill


class IntentSkill(Skill):
    """
    Detect what the user needs from their message.
    """

    name = "intent"
    description = "Detect user intent from messages"
    version = "1.0.0"

    def __init__(self):
        super().__init__()
        self._detector = None

    @property
    def actions(self) -> List[str]:
        return ["detect"]

    def _lazy_load(self):
        if self._detector is None:
            try:
                from rhea_noir.intent import IntentDetector
                self._detector = IntentDetector()
            except ImportError:
                pass

    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        self._lazy_load()

        if not self._detector:
            return self._error("Intent detector not available")

        if action == "detect":
            query = kwargs.get("query", "")
            if not query:
                return self._error("Query is required")

            has_image = kwargs.get("has_image", False)
            context = kwargs.get("context")

            result = self._detector.detect(query, has_image=has_image, context=context)
            return self._success(result)

        else:
            return self._action_not_found(action)


skill = IntentSkill()
