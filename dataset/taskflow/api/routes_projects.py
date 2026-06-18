"""Project-facing HTTP routes."""

from __future__ import annotations

from ..schemas.project import ProjectOut
from ..services.project_service import ProjectService


class ProjectRoutes:
    """Group of handlers for /projects."""

    def __init__(self, service: ProjectService) -> None:
        self.service = service

    def create_project(self, name: str, owner_id: int) -> ProjectOut:
        """POST /projects — create a project."""

        return ProjectOut.from_model(self.service.create(name, owner_id))

    def archive_project(self, project_id: int) -> ProjectOut:
        """POST /projects/{id}/archive — archive a project."""

        return ProjectOut.from_model(self.service.archive(project_id))
