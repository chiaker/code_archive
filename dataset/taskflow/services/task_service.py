"""Task lifecycle operations."""

from __future__ import annotations

from ..constants import Priority, TaskStatus
from ..models.task import Task
from ..repositories.task_repo import TaskRepository


class TaskService:
    """Create, assign and progress tasks."""

    def __init__(self, tasks: TaskRepository) -> None:
        self.tasks = tasks

    def create(self, project_id: int, title: str, priority: Priority = Priority.NORMAL) -> Task:
        """Create a new task in a project."""

        return self.tasks.add(Task(id=0, project_id=project_id, title=title, priority=priority))

    def complete(self, task_id: int) -> Task:
        """Mark a task as done."""

        task = self.tasks.get_or_raise(task_id)
        task.status = TaskStatus.DONE
        return task

    def reassign(self, task_id: int, user_id: int) -> Task:
        """Reassign a task to a different user."""

        task = self.tasks.get_or_raise(task_id)
        task.assign(user_id)
        return task

    def backlog(self, project_id: int) -> list[Task]:
        """Return not-done tasks for a project, highest priority first."""

        tasks = [t for t in self.tasks.for_project(project_id) if t.status is not TaskStatus.DONE]
        return sorted(tasks, key=lambda t: t.priority, reverse=True)
