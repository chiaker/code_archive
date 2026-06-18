"""Test helpers (note: same file name as other utils.py modules on purpose)."""

from __future__ import annotations

from ..models.task import Task


def make_task(title: str = "demo", project_id: int = 1) -> Task:
    """Build a throwaway Task for assertions."""

    return Task(id=1, project_id=project_id, title=title)


def titles(tasks: list[Task]) -> list[str]:
    """Extract titles from a list of tasks."""

    return [t.title for t in tasks]
