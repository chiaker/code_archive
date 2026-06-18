"""Repository for Project entities."""

from __future__ import annotations

from typing import Optional

from ..models.project import Project
from .base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    """Stores projects with slug lookups."""

    def find_by_slug(self, slug: str) -> Optional[Project]:
        """Return the project with a matching slug."""

        for project in self._items.values():
            if project.slug == slug:
                return project
        return None

    def active(self) -> list[Project]:
        """Return non-archived projects."""

        return list(self.filter(lambda p: not p.archived))
