"""Database service for component discovery example."""


class DatabaseService:
    """Mock database service."""

    def get_user(self, user_id: int) -> dict[str, str]:
        return {"id": str(user_id), "name": "Alice", "role": "admin"}

    def get_users_count(self) -> int:
        return 42
