"""
Rhea Noir Skills System
Following Anthropic's Agent Skills pattern for modular, discoverable capabilities.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
import importlib
import os

from .base import Skill

# Skills directory
SKILLS_DIR = Path(__file__).parent


class SkillRegistry:
    """
    Registry for managing and discovering skills.
    Supports progressive disclosure - only loads what's needed.
    """
    
    def __init__(self):
        self._skills: Dict[str, Skill] = {}
        self._loaded = False
    
    def register(self, skill: Skill):
        """Register a skill instance."""
        self._skills[skill.name] = skill
    
    def get(self, name: str) -> Optional[Skill]:
        """Get a skill by name, loading if necessary."""
        if not self._loaded:
            self._discover_skills()
        return self._skills.get(name)
    
    def all(self) -> List[Skill]:
        """Get all registered skills."""
        if not self._loaded:
            self._discover_skills()
        return list(self._skills.values())
    
    def list_names(self) -> List[str]:
        """List all skill names."""
        if not self._loaded:
            self._discover_skills()
        return list(self._skills.keys())
    
    def _discover_skills(self):
        """Auto-discover skills from subdirectories with SKILL.md."""
        if self._loaded:
            return
        
        for item in SKILLS_DIR.iterdir():
            if item.is_dir() and not item.name.startswith('_'):
                skill_md = item / "SKILL.md"
                actions_py = item / "actions.py"
                
                if skill_md.exists() or actions_py.exists():
                    try:
                        # Try to import the skill module
                        module = importlib.import_module(f".{item.name}", package=__name__)
                        if hasattr(module, 'skill'):
                            self.register(module.skill)
                    except ImportError:
                        pass
        
        self._loaded = True
    
    def to_dict(self) -> List[Dict[str, Any]]:
        """Export all skills for A2A discovery."""
        return [skill.to_dict() for skill in self.all()]


# Global registry instance
registry = SkillRegistry()


def get_skill(name: str) -> Optional[Skill]:
    """Get a skill by name."""
    return registry.get(name)


def list_skills() -> List[str]:
    """List all available skills."""
    return registry.list_names()


def execute_skill(name: str, action: str, **kwargs) -> Dict[str, Any]:
    """Execute a skill action."""
    skill = registry.get(name)
    if not skill:
        return {"error": f"Skill '{name}' not found"}
    return skill.execute(action, **kwargs)


__all__ = [
    "Skill",
    "SkillRegistry",
    "registry",
    "get_skill",
    "list_skills",
    "execute_skill",
]
