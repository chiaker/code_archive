"""Tests for TaskService."""

from __future__ import annotations

from ..constants import TaskStatus
from ..services.task_service import TaskService
from .conftest import make_task_repo


def test_create_and_complete() -> None:
    """A created task can be completed."""

    service = TaskService(make_task_repo())
    task = service.create(project_id=1, title="write docs")
    assert task.status is TaskStatus.TODO
    service.complete(task.id)
    assert task.status is TaskStatus.DONE


def test_backlog_is_priority_sorted() -> None:
    """Backlog returns open tasks ordered by priority."""

    service = TaskService(make_task_repo())
    service.create(1, "low")
    service.create(1, "high")
    backlog = service.backlog(1)
    assert len(backlog) == 2
