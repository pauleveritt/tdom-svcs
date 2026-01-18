"""Components demonstrating different dependency injection patterns."""

from dataclasses import dataclass

from svcs_di import Inject
from svcs_di.injectors.decorators import injectable
from tdom import Node
from tdom_svcs import html

from examples.component_discovery.services.auth import AuthService
from examples.component_discovery.services.database import DatabaseService


@injectable
@dataclass
class Button:
    """Simple component with no dependencies."""

    label: str = "Click me"

    def __call__(self) -> Node:
        return html(t"<button>{self.label}</button>")


@injectable
@dataclass
class UserProfile:
    """Component with single injected dependency."""

    db: Inject[DatabaseService]
    user_id: int = 1

    def __call__(self) -> Node:
        user = self.db.get_user(self.user_id)
        name = user['name']
        role = user['role']
        return html(t"<div>User: {name} ({role})</div>")


@injectable
@dataclass
class AdminPanel:
    """Component with multiple injected dependencies."""

    db: Inject[DatabaseService]
    auth: Inject[AuthService]

    def __call__(self) -> Node:
        if not self.auth.is_authenticated():
            return html(t"<div>Please log in</div>")

        if not self.auth.has_permission("admin"):
            return html(t"<div>Access denied</div>")

        user_count = self.db.get_users_count()
        user_id = self.auth.get_current_user_id()
        user = self.db.get_user(user_id)
        user_name = user['name']

        return html(t"<div>Admin Panel - {user_name}: {user_count} users</div>")
