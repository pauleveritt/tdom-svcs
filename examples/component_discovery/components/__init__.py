"""Components demonstrating different dependency injection patterns."""

from dataclasses import dataclass
from svcs_di import Inject
from svcs_di.injectors.decorators import injectable
from examples.component_discovery.services.database import DatabaseService
from examples.component_discovery.services.auth import AuthService


@injectable
@dataclass
class Button:
    """Simple component with no dependencies."""

    label: str = "Click me"

    def __call__(self) -> str:
        return f"<button>{self.label}</button>"


@injectable
@dataclass
class UserProfile:
    """Component with single injected dependency."""

    db: Inject[DatabaseService]
    user_id: int = 1

    def __call__(self) -> str:
        user = self.db.get_user(self.user_id)
        return f"<div>User: {user['name']} ({user['role']})</div>"


@injectable
@dataclass
class AdminPanel:
    """Component with multiple injected dependencies."""

    db: Inject[DatabaseService]
    auth: Inject[AuthService]

    def __call__(self) -> str:
        if not self.auth.is_authenticated():
            return "<div>Please log in</div>"

        if not self.auth.has_permission("admin"):
            return "<div>Access denied</div>"

        user_count = self.db.get_users_count()
        user_id = self.auth.get_current_user_id()
        user = self.db.get_user(user_id)

        return f"<div>Admin Panel - {user['name']}: {user_count} users</div>"
