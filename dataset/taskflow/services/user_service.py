"""User-related operations."""

from __future__ import annotations

from ..constants import Role
from ..exceptions import ValidationError
from ..models.user import User, normalize_email
from ..repositories.user_repo import UserRepository


class UserService:
    """Create and manage user accounts."""

    def __init__(self, users: UserRepository) -> None:
        self.users = users

    def register(self, email: str, display_name: str) -> User:
        """Register a new user, rejecting duplicate emails."""

        email = normalize_email(email)
        if "@" not in email:
            raise ValidationError("email", "must contain @")
        if self.users.find_by_email(email) is not None:
            raise ValidationError("email", "already registered")
        return self.users.add(User(id=0, email=email, display_name=display_name))

    def promote(self, user_id: int) -> User:
        """Promote a user to admin."""

        user = self.users.get_or_raise(user_id)
        user.role = Role.ADMIN
        return user
