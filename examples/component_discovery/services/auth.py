"""Authentication service for component discovery example."""


class AuthService:
    """Mock authentication service."""

    def get_current_user_id(self) -> int:
        return 1

    def is_authenticated(self) -> bool:
        return True

    def has_permission(self, permission: str) -> bool:
        return permission == "admin"
