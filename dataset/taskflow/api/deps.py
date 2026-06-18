"""Shared API dependencies and request context."""

from __future__ import annotations

from dataclasses import dataclass

from ..services.auth_service import AuthService
from ..models.user import User


@dataclass
class RequestContext:
    """Per-request state passed to handlers."""

    user: User | None
    locale: str = "en"

    @property
    def is_authenticated(self) -> bool:
        """Whether a user is attached to the context."""

        return self.user is not None


def current_user(auth: AuthService, token: str) -> User:
    """Resolve the current user from a token (dependency-style)."""

    return auth.resolve(token)
