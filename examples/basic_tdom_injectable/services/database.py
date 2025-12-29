"""Database service for dependency injection."""


class DatabaseService:
    """
    Example database service.

    This service can be injected into components using Inject[DatabaseService].
    """

    def __init__(self):
        """Initialize with mock data."""
        self._users = {
            1: {"id": 1, "name": "Alice", "role": "admin", "email": "alice@example.com"},
            2: {"id": 2, "name": "Bob", "role": "user", "email": "bob@example.com"},
            3: {"id": 3, "name": "Charlie", "role": "guest", "email": "charlie@example.com"},
        }

    def get_user(self, user_id: int) -> dict:
        """
        Get user by ID.

        Args:
            user_id: The user ID to look up

        Returns:
            User dictionary with id, name, role, and email
        """
        return self._users.get(
            user_id, {"id": user_id, "name": "Unknown", "role": "guest", "email": "unknown@example.com"}
        )

    def list_users(self) -> list[dict]:
        """
        List all users.

        Returns:
            List of user dictionaries
        """
        return list(self._users.values())
