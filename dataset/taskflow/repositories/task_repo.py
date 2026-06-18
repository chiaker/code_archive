"""Repository for Task entities."""

from __future__ import annotations

from ..constants import TaskStatus
from ..models.task import Task
from .base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    """Stores tasks with project- and status-scoped queries."""

    def for_project(self, project_id: int) -> list[Task]:
        """Return all tasks belonging to a project."""

        return list(self.filter(lambda t: t.project_id == project_id))

    def by_status(self, status: TaskStatus) -> list[Task]:
        """Return tasks in a given status."""

        return list(self.filter(lambda t: t.status is status))

    def assigned_to(self, user_id: int) -> list[Task]:
        """Return tasks assigned to a user."""

        return list(self.filter(lambda t: t.assignee_id == user_id))
