"""Tag domain model."""

from __future__ import annotations

from dataclasses import dataclass

from ..db.base import Base


@dataclass
class Tag(Base):
    """A label that can be attached to tasks."""

    id: int
    name: str
    color: str = "#888888"

    def rename(self, name: str) -> None:
        """Rename the tag."""

        self.name = name


def parse_tags(raw: str) -> list[str]:
    """Split a comma-separated tag string into clean names."""

    return [part.strip() for part in raw.split(",") if part.strip()]
