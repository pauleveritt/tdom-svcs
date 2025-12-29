"""Dashboard component."""

from dataclasses import dataclass

from svcs_di import Inject
from svcs_di.injectors.decorators import injectable

from basic_tdom_injectable.services.auth import AuthService
from basic_tdom_injectable.services.database import DatabaseService


@injectable
@dataclass
class Dashboard:
    """
    Dashboard component with multiple injected dependencies.

    This component demonstrates:
    - Multiple Inject[] dependencies
    - Using multiple services together
    - Conditional rendering based on authentication

    Both db and auth are automatically injected by the DI container.
    """

    db: Inject[DatabaseService]
    auth: Inject[AuthService]

    def render(self) -> str:
        """
        Render the dashboard as HTML.

        Returns:
            HTML string for the dashboard
        """
        if not self.auth.is_authenticated():
            return '<div class="alert alert-warning">Please log in to view the dashboard.</div>'

        # Get current user
        user_id = self.auth.get_current_user_id()
        user = self.db.get_user(user_id)

        # Get all users
        users = self.db.list_users()

        users_html = "\n".join([f"<li>{u['name']} - {u['role']}</li>" for u in users])

        return f"""
        <div class="dashboard">
            <h2>Welcome, {user["name"]}!</h2>
            <p>Your role: {user["role"]}</p>
            <h3>All Users:</h3>
            <ul>
                {users_html}
            </ul>
        </div>
        """

    def __call__(self) -> str:
        """Allow component to be called directly."""
        return self.render()
