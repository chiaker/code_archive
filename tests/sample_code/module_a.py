"""Sample module for indexer tests."""


def alpha(x):
    """Return x unchanged."""
    return x


async def beta():
    """Async sample."""
    return 1


class Widget:
    """A sample class."""

    def render(self):
        """Render the widget."""

        def helper():
            """Nested helper."""
            return 0

        return helper()
