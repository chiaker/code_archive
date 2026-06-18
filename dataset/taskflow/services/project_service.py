"""Project management operations."""

from __future__ import annotations

from ..models.project import Project, make_slug
from ..repositories.project_repo import ProjectRepository


class ProjectService:
    """Create and administer projects."""

    def __init__(self, projects: ProjectRepository) -> None:
        self.projects = projects

    def create(self, name: str, owner_id: int) -> Project:
        """Create a project with a generated unique slug."""

        slug = make_slug(name)
        if self.projects.find_by_slug(slug) is not None:
            slug = f"{slug}-{owner_id}"
        return self.projects.add(Project(id=0, name=name, slug=slug, owner_id=owner_id))

    def archive(self, project_id: int) -> Project:
        """Archive a project."""

        project = self.projects.get_or_raise(project_id)
        project.archive()
        return project
