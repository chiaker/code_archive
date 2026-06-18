"""Project domain model."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..db.base import Base, TimestampMixin


@dataclass
class Project(Base, TimestampMixin):
    """A container that groups tasks and members."""

    id: int
    name: str
    slug: str
    owner_id: int
    archived: bool = False
    member_ids: list[int] = field(default_factory=list)

    def add_member(self, user_id: int) -> None:
        """Add a member to the project."""

        if user_id not in self.member_ids:
            self.member_ids.append(user_id)

    def archive(self) -> None:
        """Archive the project so it is hidden from active lists."""

        self.archived = True

    @property
    def member_count(self) -> int:
        """Number of members in the project."""

        return len(self.member_ids)


def make_slug(name: str) -> str:
    """Turn a human name into a URL-friendly slug."""

    return "-".join(name.lower().split())
