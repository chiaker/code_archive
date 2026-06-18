"""User-facing HTTP routes."""

from __future__ import annotations

from ..schemas.user import UserCreate, UserOut
from ..services.user_service import UserService


class UserRoutes:
    """Group of handlers for /users."""

    def __init__(self, service: UserService) -> None:
        self.service = service

    def create_user(self, payload: UserCreate) -> UserOut:
        """POST /users — register a new account."""

        user = self.service.register(payload.email, payload.display_name)
        return UserOut.from_model(user)

    def list_users(self) -> list[UserOut]:
        """GET /users — list active users."""

        return [UserOut.from_model(u) for u in self.service.users.active_users()]
