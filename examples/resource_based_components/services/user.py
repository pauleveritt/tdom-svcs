"""User service for retrieving user information."""


class UserService:
    """Mock user service."""

    def get_current_user(self) -> dict[str, str]:
        return {"name": "Alice", "role": "customer"}
