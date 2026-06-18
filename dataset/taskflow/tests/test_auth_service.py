"""Tests for password hashing and AuthService."""

from __future__ import annotations

from ..services.auth_service import hash_password, verify_password


def test_password_roundtrip() -> None:
    """A hashed password verifies against the original."""

    hashed = hash_password("s3cret")
    assert verify_password("s3cret", hashed)
    assert not verify_password("wrong", hashed)
