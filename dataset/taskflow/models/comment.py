"""Comment domain model."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ..db.base import Base


@dataclass
class Comment(Base):
    """A comment left by a user on a task."""

    id: int
    task_id: int
    author_id: int
    body: str
    created_at: datetime

    def edit(self, body: str) -> None:
        """Replace the comment body."""

        self.body = body

    @property
    def preview(self) -> str:
        """A short single-line preview of the comment."""

        return self.body.strip().splitlines()[0][:80] if self.body else ""
