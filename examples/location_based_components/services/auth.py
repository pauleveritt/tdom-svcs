"""Authentication service for location-based components."""


class AuthService:
    """Mock authentication service."""

    def get_current_user(self) -> str:
        return "admin_user"

    def is_admin(self) -> bool:
        return True
