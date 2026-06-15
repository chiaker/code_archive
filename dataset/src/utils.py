"""Shared utilities."""


def normalize_name(raw_name: str) -> str:
    """Normalize a name for display."""

    return " ".join(raw_name.split()).title()


async def load_remote_config():
    """Pretend to load configuration remotely."""

    return {"source": "remote"}

