"""
Rhea Noir Task Harness - Long-running task management
Enables background tasks that can continue after CLI closes
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from enum import Enum


class TaskStatus(Enum):
    """Task status states"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Task:
    """A single long-running task"""

    def __init__(
        self,
        description: str,
        task_type: str = "general",
        priority: int = 5,
        task_id: Optional[str] = None
    ):
        self.id = task_id or str(uuid.uuid4())[:8]
        self.description = description
        self.task_type = task_type
        self.priority = priority
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now().isoformat()
        self.started_at: Optional[str] = None
        self.completed_at: Optional[str] = None
        self.result: Optional[str] = None
        self.error: Optional[str] = None
        self.progress: float = 0.0
        self.logs: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "task_type": self.task_type,
            "priority": self.priority,
            "status": self.status.value,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "result": self.result,
            "error": self.error,
            "progress": self.progress,
            "logs": self.logs[-10:],  # Keep last 10 log entries
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        task = cls(
            description=data["description"],
            task_type=data.get("task_type", "general"),
            priority=data.get("priority", 5),
            task_id=data["id"]
        )
        task.status = TaskStatus(data["status"])
        task.created_at = data["created_at"]
        task.started_at = data.get("started_at")
        task.completed_at = data.get("completed_at")
        task.result = data.get("result")
        task.error = data.get("error")
        task.progress = data.get("progress", 0.0)
        task.logs = data.get("logs", [])
        return task

    def log(self, message: str):
        """Add a log entry"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs.append(f"[{timestamp}] {message}")

    def start(self):
        """Mark task as started"""
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.now().isoformat()
        self.log("Task started")

    def complete(self, result: str):
        """Mark task as completed"""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now().isoformat()
        self.result = result
        self.progress = 1.0
        self.log("Task completed")

    def fail(self, error: str):
        """Mark task as failed"""
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.now().isoformat()
        self.error = error
        self.log(f"Task failed: {error}")

    def cancel(self):
        """Mark task as cancelled"""
        self.status = TaskStatus.CANCELLED
        self.completed_at = datetime.now().isoformat()
        self.log("Task cancelled")


class TaskHarness:
    """Manages long-running tasks with persistence"""

    def __init__(self, data_dir: Optional[str] = None):
        """Initialize task harness"""
        if data_dir is None:
            data_dir = Path.home() / ".rhea_noir" / "harness"

        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.task_list_file = self.data_dir / "task_list.json"
        self.progress_file = self.data_dir / "rhea_progress.json"

        self.tasks: Dict[str, Task] = {}
        self._load()

    def _load(self):
        """Load tasks from disk"""
        if self.task_list_file.exists():
            with open(self.task_list_file, encoding="utf-8") as f:
                data = json.load(f)
                for task_data in data.get("tasks", []):
                    task = Task.from_dict(task_data)
                    self.tasks[task.id] = task

    def _save(self):
        """Save tasks to disk"""
        data = {
            "tasks": [t.to_dict() for t in self.tasks.values()],
            "last_updated": datetime.now().isoformat(),
        }
        with open(self.task_list_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _log_progress(self, task: Task, action: str):
        """Log progress to rhea_progress.json"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "task_id": task.id,
            "action": action,
            "status": task.status.value,
            "description": task.description[:50],
        }

        # Load existing progress
        progress = []
        if self.progress_file.exists():
            with open(self.progress_file, encoding="utf-8") as f:
                progress = json.load(f).get("entries", [])

        progress.append(entry)

        # Keep last 100 entries
        progress = progress[-100:]

        with open(self.progress_file, "w", encoding="utf-8") as f:
            json.dump({"entries": progress}, f, indent=2)

    def create_task(self, description: str, task_type: str = "general") -> Task:
        """Create a new task"""
        task = Task(description=description, task_type=task_type)
        self.tasks[task.id] = task
        self._save()
        self._log_progress(task, "created")
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID"""
        return self.tasks.get(task_id)

    def list_tasks(self, status: Optional[TaskStatus] = None) -> List[Task]:
        """List tasks, optionally filtered by status"""
        tasks = list(self.tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        return sorted(tasks, key=lambda t: t.created_at, reverse=True)

    def get_pending_tasks(self) -> List[Task]:
        """Get all pending tasks"""
        return self.list_tasks(TaskStatus.PENDING)

    def get_running_tasks(self) -> List[Task]:
        """Get all running tasks"""
        return self.list_tasks(TaskStatus.RUNNING)

    def start_task(self, task_id: str) -> bool:
        """Start a pending task"""
        task = self.tasks.get(task_id)
        if task and task.status == TaskStatus.PENDING:
            task.start()
            self._save()
            self._log_progress(task, "started")
            return True
        return False

    def complete_task(self, task_id: str, result: str) -> bool:
        """Complete a running task"""
        task = self.tasks.get(task_id)
        if task and task.status == TaskStatus.RUNNING:
            task.complete(result)
            self._save()
            self._log_progress(task, "completed")
            return True
        return False

    def fail_task(self, task_id: str, error: str) -> bool:
        """Mark a task as failed"""
        task = self.tasks.get(task_id)
        if task and task.status == TaskStatus.RUNNING:
            task.fail(error)
            self._save()
            self._log_progress(task, "failed")
            return True
        return False

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a task"""
        task = self.tasks.get(task_id)
        if task and task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            task.cancel()
            self._save()
            self._log_progress(task, "cancelled")
            return True
        return False

    def update_progress(self, task_id: str, progress: float, log_message: Optional[str] = None):
        """Update task progress"""
        task = self.tasks.get(task_id)
        if task:
            task.progress = min(max(progress, 0.0), 1.0)
            if log_message:
                task.log(log_message)
            self._save()

    def get_stats(self) -> Dict[str, int]:
        """Get task statistics"""
        stats = {
            "total": len(self.tasks),
            "pending": 0,
            "running": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0,
        }
        for task in self.tasks.values():
            stats[task.status.value] = stats.get(task.status.value, 0) + 1
        return stats


# Global harness instance
harness = TaskHarness()
