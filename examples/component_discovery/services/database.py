"""Database service."""


class DatabaseService:
    """Example database service."""

    def get_user(self, user_id: int) -> dict:
        """Get user by ID."""
        users = {
            1: {"id": 1, "name": "Alice", "role": "admin"},
            2: {"id": 2, "name": "Bob", "role": "user"},
            3: {"id": 3, "name": "Charlie", "role": "guest"},
        }
        return users.get(user_id, {"id": user_id, "name": "Unknown", "role": "guest"})
