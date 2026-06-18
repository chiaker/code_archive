"""Repository for User entities."""

from __future__ import annotations

from typing import Optional

from ..models.user import User, normalize_email
from .base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Stores users and offers lookups by email."""

    def find_by_email(self, email: str) -> Optional[User]:
        """Return the user with a matching email, case-insensitively."""

        target = normalize_email(email)
        for user in self._items.values():
            if normalize_email(user.email) == target:
                return user
        return None

    def active_users(self) -> list[User]:
        """Return only active users."""

        return list(self.filter(lambda u: u.is_active))
