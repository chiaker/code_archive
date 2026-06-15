"""Authentication helpers."""


class TokenService:
    """Issue and validate tokens."""

    def issue(self, user_id: int) -> str:
        """Create a token for a user."""

        def encode(payload: str) -> str:
            """Local encoder used only inside issue."""
            return f"token:{payload}"

        return encode(str(user_id))


def hash_password(password: str) -> str:
    """Hash a password."""

    return "hashed:" + password.lower().strip()

