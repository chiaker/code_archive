"""Authentication and token handling."""

from __future__ import annotations

import hashlib
import secrets

from ..exceptions import PermissionDeniedError
from ..models.user import User
from ..repositories.user_repo import UserRepository


def hash_password(password: str, salt: str | None = None) -> str:
    """Hash a password with a random or provided salt."""

    salt = salt or secrets.token_hex(8)
    digest = hashlib.sha256(f"{salt}:{password}".encode()).hexdigest()
    return f"{salt}${digest}"


def verify_password(password: str, hashed: str) -> bool:
    """Check a plaintext password against a stored hash."""

    salt, _, _ = hashed.partition("$")
    return hash_password(password, salt) == hashed


class AuthService:
    """Coordinates login and token issuance for users."""

    def __init__(self, users: UserRepository) -> None:
        self.users = users
        self._sessions: dict[str, int] = {}

    def login(self, email: str, password: str, expected_hash: str) -> str:
        """Authenticate a user and return a session token."""

        user = self.users.find_by_email(email)
        if user is None or not verify_password(password, expected_hash):
            raise PermissionDeniedError("invalid credentials")
        token = secrets.token_urlsafe(16)
        self._sessions[token] = user.id
        return token

    def resolve(self, token: str) -> User:
        """Return the user behind a session token."""

        user_id = self._sessions.get(token)
        if user_id is None:
            raise PermissionDeniedError("invalid token")
        return self.users.get_or_raise(user_id)

    def logout(self, token: str) -> None:
        """Invalidate a session token."""

        self._sessions.pop(token, None)
