"""API service layer."""


class ApiClient:
    """Talks to an external API."""

    async def fetch_users(self, limit: int = 10):
        """Fetch users from the upstream service."""
        return [{"id": i} for i in range(limit)]

    def _build_headers(self):
        """Build headers."""
        return {"Accept": "application/json"}


def create_client() -> ApiClient:
    """Factory for ApiClient."""
    return ApiClient()

