"""Task domain model — the core entity of the app."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from ..constants import Priority, TaskStatus
from ..db.base import Base, TimestampMixin


@dataclass
class Task(Base, TimestampMixin):
    """A unit of work belonging to a project."""

    id: int
    project_id: int
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.TODO
    priority: Priority = Priority.NORMAL
    assignee_id: int | None = None
    tag_ids: list[int] = field(default_factory=list)
    due_at: datetime | None = None

    def assign(self, user_id: int) -> None:
        """Assign the task to a user."""

        self.assignee_id = user_id

    def advance(self) -> TaskStatus:
        """Move the task to the next status in its lifecycle."""

        order = [
            TaskStatus.TODO,
            TaskStatus.IN_PROGRESS,
            TaskStatus.DONE,
        ]
        if self.status in order and self.status is not TaskStatus.DONE:
            self.status = order[order.index(self.status) + 1]
        return self.status

    @property
    def is_overdue(self) -> bool:
        """Whether the task is past its due date and not done."""

        if self.due_at is None or self.status is TaskStatus.DONE:
            return False
        return self.due_at < datetime.utcnow()


def is_high_priority(task: Task) -> bool:
    """Return True for high or critical priority tasks."""

    return task.priority in (Priority.HIGH, Priority.CRITICAL)
