"""Database service for dependency injection."""


class DatabaseService:
    """
    Example database service.

    This service can be injected into components using Inject[DatabaseService].
    """

    def __init__(self):
        """Initialize with mock data."""
        self._users = {
            1: {"id": 1, "name": "Alice", "role": "admin"},
            2: {"id": 2, "name": "Bob", "role": "user"},
            3: {"id": 3, "name": "Charlie", "role": "guest"},
        }

    def get_user(self, user_id: int) -> dict:
        """
        Get user by ID.

        Args:
            user_id: The user ID to look up

        Returns:
            User dictionary with id, name, and role
        """
        return self._users.get(
            user_id, {"id": user_id, "name": "Unknown", "role": "guest"}
        )

    def list_users(self) -> list[dict]:
        """
        List all users.

        Returns:
            List of user dictionaries
        """
        return list(self._users.values())

    def get_status(self) -> str:
        """
        Get database connection status.

        Returns:
            Status string
        """
        return "connected"
