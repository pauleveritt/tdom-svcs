"""Authentication service for dependency injection."""


class AuthService:
    """
    Example authentication service.

    This service can be injected into components to check authentication state.
    """

    def __init__(self):
        """Initialize with mock authentication state."""
        self._authenticated = True
        self._current_user_id = 1

    def is_authenticated(self) -> bool:
        """
        Check if current user is authenticated.

        Returns:
            True if authenticated, False otherwise
        """
        return self._authenticated

    def get_current_user_id(self) -> int:
        """
        Get the current authenticated user ID.

        Returns:
            User ID of the current user
        """
        return self._current_user_id

    def login(self, user_id: int) -> bool:
        """
        Simulate user login.

        Args:
            user_id: The user ID to log in as

        Returns:
            True if login successful
        """
        self._authenticated = True
        self._current_user_id = user_id
        return True

    def logout(self) -> None:
        """Simulate user logout."""
        self._authenticated = False
        self._current_user_id = 0
