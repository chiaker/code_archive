"""Project request/response schemas."""

from __future__ import annotations

from dataclasses import dataclass

from ..models.project import Project


@dataclass
class ProjectOut:
    """Public representation of a project."""

    id: int
    name: str
    slug: str
    member_count: int

    @classmethod
    def from_model(cls, project: Project) -> "ProjectOut":
        """Build a schema from a Project model."""

        return cls(id=project.id, name=project.name, slug=project.slug, member_count=project.member_count)
