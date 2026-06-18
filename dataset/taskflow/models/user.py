"""User domain model."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..constants import Role
from ..db.base import Base, TimestampMixin


@dataclass
class User(Base, TimestampMixin):
    """A registered account."""

    id: int
    email: str
    display_name: str
    role: Role = Role.MEMBER
    is_active: bool = True
    project_ids: list[int] = field(default_factory=list)

    @property
    def is_admin(self) -> bool:
        """Whether this user has the admin role."""

        return self.role is Role.ADMIN

    def deactivate(self) -> None:
        """Mark the account as inactive."""

        self.is_active = False

    def join_project(self, project_id: int) -> None:
        """Add the user to a project if not already a member."""

        if project_id not in self.project_ids:
            self.project_ids.append(project_id)


def normalize_email(email: str) -> str:
    """Lower-case and strip an email address."""

    return email.strip().lower()
