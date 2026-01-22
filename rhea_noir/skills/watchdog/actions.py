"""
Watchdog Skill: Meta-Agent Orchestration using Vertex AI Reasoning Engine.
"""

from typing import List, Dict, Any, Optional
import os
import json

try:
    from google.cloud import aiplatform
    from vertexai.preview import reasoning_engines
except ImportError:
    aiplatform = None
    reasoning_engines = None

class WatchdogSkill:
    """
    Oversight agent for Ralph Loop and long-running autonomous tasks.
    """
    
    name = "watchdog"
    description = "Autonomous meta-agent for monitoring Ralph Loop tasks."
    version = "1.0.0"
    ENGINE_RESOURCE_NAME = "projects/145241643240/locations/us-central1/reasoningEngines/3069691329215725568"

    def __init__(self):
        self._engine = None

    @property
    def actions(self) -> List[str]:
        """List of available actions."""
        return [
            "monitor_task",
            "recovery_directive",
            "get_engine_metadata"
        ]

    def _get_engine(self):
        """Lazy load the reasoning engine resource."""
        if self._engine is None and reasoning_engines is not None:
            try:
                self._engine = reasoning_engines.ReasoningEngine(self.ENGINE_RESOURCE_NAME)
            except Exception as e:
                print(f"⚠️ Failed to load Reasoning Engine: {e}")
        return self._engine

    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute a watchdog action."""
        try:
            if action == "monitor_task":
                return self._monitor_task(kwargs.get("task_id"), kwargs.get("history"))
            if action == "recovery_directive":
                return self._recovery_directive(kwargs.get("goal"), kwargs.get("context"))
            if action == "get_engine_metadata":
                return self._get_engine_metadata()
            return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _monitor_task(self, task_id: str, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze a Ralph Loop task for stalls or regressions."""
        if not history:
            return {"status": "healthy", "recommendation": "continue"}
        
        # Heuristic: Check for identical errors in consecutive iterations
        if len(history) >= 2:
            last = history[-1].get("errors", "")
            prev = history[-2].get("errors", "")
            if last == prev and last != "":
                return {
                    "status": "stalled",
                    "recommendation": "trigger_recovery",
                    "reason": "Repeated verification errors."
                }
        
        return {"status": "healthy", "recommendation": "continue"}

    def _recovery_directive(self, goal: str, context: str) -> Dict[str, Any]:
        """Query the remote Reasoning Engine for a recovery strategy."""
        engine = self._get_engine()
        if not engine:
            return {"success": False, "error": "Reasoning Engine unavailable."}

        # The 'query' method is the standard interface for Reasoning Engines
        try:
            response = engine.query(input={
                "task": "RECOVERY_ORCHESTRATION",
                "goal": goal,
                "context": context
            })
            return {"success": True, "recovery_plan": response}
        except Exception as e:
            return {"success": False, "error": f"Engine Query Failed: {e}"}

    def _get_engine_metadata(self) -> Dict[str, Any]:
        """Get info about the Vertex AI chassis."""
        engine = self._get_engine()
        if not engine:
            return {"success": False, "error": "Engine not initialized."}
        
        return {
            "success": True,
            "resource_name": self.ENGINE_RESOURCE_NAME,
            "engine_id": self.ENGINE_RESOURCE_NAME.split("/")[-1],
            "adk_version": "1.14.1 (local)"
        }

# Global instance for registration
skill = WatchdogSkill()
