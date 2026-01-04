"""Location-based page components."""

from dataclasses import dataclass
from pathlib import PurePath
from svcs_di import Inject
from svcs_di.injectors.decorators import injectable
from examples.location_based_components.services.auth import AuthService
from examples.location_based_components.services.content import ContentService


@injectable(location=PurePath("/admin"))
@dataclass
class AdminPanel:
    """Admin panel for /admin location."""

    auth: Inject[AuthService]

    def __call__(self) -> str:
        if not self.auth.is_admin():
            return "<div>Access Denied</div>"
        user = self.auth.get_current_user()
        return f"<div>Admin Panel: {user}</div>"


@injectable(location=PurePath("/admin/users"))
@dataclass
class UserManagement:
    """User management panel for /admin/users location."""

    auth: Inject[AuthService]

    def __call__(self) -> str:
        return "<div>User Management</div>"


@injectable(location=PurePath("/"))
@dataclass
class HomePage:
    """Home page for / location."""

    content: Inject[ContentService]

    def __call__(self) -> str:
        page_content = self.content.get_page_content("/")
        return f"<div>Home: {page_content}</div>"
