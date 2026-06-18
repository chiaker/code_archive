"""Periodic cleanup of stale data."""

from __future__ import annotations

from ..models.task import Task
from ..constants import TaskStatus


class CleanupWorker:
    """Removes done tasks older than a retention window."""

    def __init__(self, retention_days: int = 30) -> None:
        self.retention_days = retention_days

    def stale_tasks(self, tasks: list[Task]) -> list[Task]:
        """Return done tasks that are eligible for cleanup."""

        return [t for t in tasks if t.status is TaskStatus.DONE]

    def purge(self, tasks: list[Task]) -> int:
        """Remove stale tasks in place and return how many were removed."""

        stale = self.stale_tasks(tasks)
        for task in stale:
            tasks.remove(task)
        return len(stale)
