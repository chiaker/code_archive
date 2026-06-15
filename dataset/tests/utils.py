"""Test helpers with the same basename as src/utils.py."""


def make_user(name: str):
    """Build a fake user."""
    return {"name": name}


class FakeRepo:
    """A fake repository used in tests."""

    def add(self, item):
        """Store a thing."""
        self.item = item

