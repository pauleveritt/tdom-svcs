"""User profile component."""

from dataclasses import dataclass

from svcs_di import Inject
from svcs_di.injectors.decorators import injectable

from component_discovery.services.database import DatabaseService


@injectable
@dataclass
class UserProfile:
    """
    User profile component with injected dependencies.

    The 'db' parameter uses Inject[DatabaseService] which tells the injector
    to resolve DatabaseService from the svcs container. Regular parameters
    like 'user_id' have default values but can be overridden from templates.
    """

    db: Inject[DatabaseService]  # Injected from container
    user_id: int = 1  # Default value, can be overridden from template

    def __call__(self) -> str:
        """Render the user profile with data from database."""
        user = self.db.get_user(self.user_id)
        return f"""
        <div class="user-profile">
            <h2>{user['name']}</h2>
            <p>ID: {user['id']}</p>
            <p>Role: {user['role']}</p>
        </div>
        """.strip()
