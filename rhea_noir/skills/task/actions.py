"""
Task Skill - Long-running task management.
"""

from typing import Dict, List, Any
from ..base import Skill


class TaskSkill(Skill):
    """
    Manage background tasks that persist across sessions.
    """

    name = "task"
    description = "Manage long-running background tasks"
    version = "1.0.0"

    def __init__(self):
        super().__init__()
        self._harness = None

    @property
    def actions(self) -> List[str]:
        return ["create", "start", "status", "list", "complete", "fail", "stats"]

    def _lazy_load(self):
        if self._harness is None:
            try:
                from rhea_noir.harness import TaskHarness
                self._harness = TaskHarness()
            except ImportError:
                pass

    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        self._lazy_load()

        if not self._harness:
            return self._error("Task harness not available")

        if action == "create":
            desc = kwargs.get("description", "")
            if not desc:
                return self._error("Description required")
            task = self._harness.create_task(desc, kwargs.get("task_type", "general"))
            return self._success({"task_id": task.task_id, "status": task.status.value})

        elif action == "start":
            task_id = kwargs.get("task_id", "")
            task = self._harness.start_task(task_id)
            return self._success(task.to_dict()) if task else self._error("Task not found")

        elif action == "status":
            task_id = kwargs.get("task_id", "")
            task = self._harness.get_task(task_id)
            return self._success(task.to_dict()) if task else self._error("Task not found")

        elif action == "list":
            tasks = self._harness.list_tasks()
            return self._success({"tasks": [t.to_dict() for t in tasks]})

        elif action == "complete":
            task_id = kwargs.get("task_id", "")
            result = kwargs.get("result", "")
            task = self._harness.complete_task(task_id, result)
            return self._success(task.to_dict()) if task else self._error("Task not found")

        elif action == "fail":
            task_id = kwargs.get("task_id", "")
            error = kwargs.get("error", "")
            task = self._harness.fail_task(task_id, error)
            return self._success(task.to_dict()) if task else self._error("Task not found")

        elif action == "stats":
            stats = self._harness.get_stats()
            return self._success(stats)

        else:
            return self._action_not_found(action)


skill = TaskSkill()
