"""
Expressions Skill - Rhea's emoji personality.
"""

from typing import Dict, List, Any
from ..base import Skill


class ExpressionsSkill(Skill):
    """
    Rhea's dark skin tone emoji system.
    """
    
    name = "expressions"
    description = "Rhea's emoji and expression system"
    version = "1.0.0"
    
    def __init__(self):
        super().__init__()
        self._expr = None
    
    @property
    def actions(self) -> List[str]:
        return ["hand", "reaction", "signature", "all"]
    
    def _lazy_load(self):
        if self._expr is None:
            try:
                from rhea_noir.expressions import (
                    RheaExpressions, get_hand, get_reaction, get_signature
                )
                self._expr = RheaExpressions()
                self._get_hand = get_hand
                self._get_reaction = get_reaction
                self._get_signature = get_signature
            except ImportError:
                pass
    
    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        self._lazy_load()
        
        if not self._expr:
            return self._error("Expressions not available")
        
        if action == "hand":
            gesture = kwargs.get("gesture", "wave")
            emoji = self._get_hand(gesture)
            return self._success({"emoji": emoji, "gesture": gesture})
        
        elif action == "reaction":
            mood = kwargs.get("mood", "happy")
            emoji = self._get_reaction(mood)
            return self._success({"emoji": emoji, "mood": mood})
        
        elif action == "signature":
            sig = self._get_signature()
            return self._success({"signature": sig})
        
        elif action == "all":
            return self._success({
                "hands": self._expr.DARK_HANDS if hasattr(self._expr, 'DARK_HANDS') else {},
                "reactions": self._expr.REACTIONS if hasattr(self._expr, 'REACTIONS') else {},
            })
        
        else:
            return self._action_not_found(action)


skill = ExpressionsSkill()
