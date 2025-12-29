"""Authentication service."""


class AuthService:
    """Example authentication service."""

    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return True

    def get_current_role(self) -> str:
        """Get current user's role."""
        return "admin"
