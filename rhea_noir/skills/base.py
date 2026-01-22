"""
Rhea Noir Skill Base Class
Following Anthropic's Agent Skills pattern.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Any, Optional


class Skill(ABC):
    """
    Base class for all Rhea skills.

    A skill is a modular capability that can be:
    - Discovered via A2A
    - Loaded progressively (only when needed)
    - Executed with specific actions

    Directory structure:
        skills/
        └── skill_name/
            ├── SKILL.md      # Instructions + metadata
            ├── actions.py    # This file with Skill subclass
            └── resources/    # Optional assets
    """

    # Override in subclasses
    name: str = "base"
    description: str = "Base skill"
    version: str = "1.0.0"

    def __init__(self):
        self._instructions: Optional[str] = None
        self._skill_dir = Path(__file__).parent / self.name

    @property
    def actions(self) -> List[str]:
        """List of available actions. Override in subclass."""
        return []

    @abstractmethod
    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a skill action.

        Args:
            action: The action to perform (must be in self.actions)
            **kwargs: Action-specific parameters

        Returns:
            Dict with 'success', 'result', and optionally 'error'
        """
        pass

    def load_instructions(self) -> str:
        """
        Load SKILL.md instructions (progressive disclosure).
        Only loaded on first access.
        """
        if self._instructions is None:
            skill_md = self._skill_dir / "SKILL.md"
            if skill_md.exists():
                self._instructions = skill_md.read_text(encoding="utf-8")
            else:
                self._instructions = f"# {self.name}\n\n{self.description}"
        return self._instructions

    def to_dict(self) -> Dict[str, Any]:
        """Export skill metadata for A2A discovery."""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "actions": self.actions,
        }

    def _success(self, result: Any) -> Dict[str, Any]:
        """Helper to return success response."""
        return {"success": True, "result": result}

    def _error(self, message: str) -> Dict[str, Any]:
        """Helper to return error response."""
        return {"success": False, "error": message}

    def _action_not_found(self, action: str) -> Dict[str, Any]:
        """Helper for unknown action."""
        return self._error(f"Unknown action '{action}'. Available: {self.actions}")
