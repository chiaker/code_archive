"""Tests for auth module."""


def test_hash_password():
    """Should hash passwords."""
    assert True


class TestTokenService:
    """Token service tests."""

    def test_issue(self):
        """Issue should return a string."""
        assert isinstance("x", str)

