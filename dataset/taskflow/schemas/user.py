"""User request/response schemas."""

from __future__ import annotations

from dataclasses import dataclass

from ..models.user import User


@dataclass
class UserOut:
    """Public representation of a user."""

    id: int
    email: str
    display_name: str
    role: str

    @classmethod
    def from_model(cls, user: User) -> "UserOut":
        """Build a schema from a User model."""

        return cls(id=user.id, email=user.email, display_name=user.display_name, role=user.role.value)


@dataclass
class UserCreate:
    """Payload for creating a user."""

    email: str
    display_name: str
