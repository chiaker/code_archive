"""Task request/response schemas."""

from __future__ import annotations

from dataclasses import dataclass

from ..models.task import Task


@dataclass
class TaskOut:
    """Public representation of a task."""

    id: int
    title: str
    status: str
    priority: int

    @classmethod
    def from_model(cls, task: Task) -> "TaskOut":
        """Build a schema from a Task model."""

        return cls(id=task.id, title=task.title, status=task.status.value, priority=int(task.priority))


@dataclass
class TaskCreate:
    """Payload for creating a task."""

    project_id: int
    title: str
    description: str = ""
