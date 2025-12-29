"""Admin panel component."""

from dataclasses import dataclass

from svcs_di import Inject
from svcs_di.injectors.decorators import injectable

from component_discovery.services.auth import AuthService
from component_discovery.services.database import DatabaseService


@injectable
@dataclass
class AdminPanel:
    """
    Admin panel component with multiple injected dependencies.

    This demonstrates that multiple dependencies can be injected,
    and regular parameters can be mixed with injected ones.
    """

    auth: Inject[AuthService]
    db: Inject[DatabaseService]
    title: str = "Admin Dashboard"

    def __call__(self) -> str:
        """Render the admin panel with authentication check."""
        if not self.auth.is_authenticated():
            return "<p>Access denied. Please log in.</p>"

        role = self.auth.get_current_role()
        user = self.db.get_user(1)

        return f"""
        <div class="admin-panel">
            <h1>{self.title}</h1>
            <p>Current user: {user['name']} ({role})</p>
            <p>Admin features would go here...</p>
        </div>
        """.strip()
