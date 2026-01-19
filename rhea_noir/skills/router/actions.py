"""
Router Skill - Model tier selection.
"""

from typing import Dict, List, Any
from ..base import Skill


class RouterSkill(Skill):
    """
    Select appropriate Gemini model tier.
    """
    
    name = "router"
    description = "Select AI model tier based on complexity"
    version = "1.0.0"
    
    def __init__(self):
        super().__init__()
        self._router = None
    
    @property
    def actions(self) -> List[str]:
        return ["route", "list"]
    
    def _lazy_load(self):
        if self._router is None:
            try:
                from rhea_noir.router import ModelRouter
                self._router = ModelRouter()
            except ImportError:
                pass
    
    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        self._lazy_load()
        
        if not self._router:
            return self._error("Router not available")
        
        if action == "route":
            query = kwargs.get("query", "")
            has_image = kwargs.get("has_image", False)
            model_name, location, tier = self._router.route(query, has_image)
            return self._success({
                "model": model_name,
                "location": location,
                "tier": tier.value,
            })
        
        elif action == "list":
            models = self._router.list_models()
            return self._success({"models": models})
        
        else:
            return self._action_not_found(action)


skill = RouterSkill()
