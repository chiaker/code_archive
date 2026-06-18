"""Task-facing HTTP routes."""

from __future__ import annotations

from ..schemas.task import TaskCreate, TaskOut
from ..services.task_service import TaskService


class TaskRoutes:
    """Group of handlers for /tasks."""

    def __init__(self, service: TaskService) -> None:
        self.service = service

    def create_task(self, payload: TaskCreate) -> TaskOut:
        """POST /tasks — create a task."""

        task = self.service.create(payload.project_id, payload.title)
        return TaskOut.from_model(task)

    def complete_task(self, task_id: int) -> TaskOut:
        """POST /tasks/{id}/complete — mark a task done."""

        return TaskOut.from_model(self.service.complete(task_id))

    def project_backlog(self, project_id: int) -> list[TaskOut]:
        """GET /projects/{id}/backlog — open tasks by priority."""

        return [TaskOut.from_model(t) for t in self.service.backlog(project_id)]
