"""Location-based page components."""

from dataclasses import dataclass
from pathlib import PurePath

from svcs_di import Inject
from svcs_di.injectors.decorators import injectable
from tdom import Node
from tdom_svcs import html

from examples.location_based_components.services.auth import AuthService
from examples.location_based_components.services.content import ContentService


@injectable(location=PurePath("/admin"))
@dataclass
class AdminPanel:
    """Admin panel for /admin location."""

    auth: Inject[AuthService]

    def __call__(self) -> Node:
        if not self.auth.is_admin():
            return html(t"<div>Access Denied</div>")
        user = self.auth.get_current_user()
        return html(t"<div>Admin Panel: {user}</div>")


@injectable(location=PurePath("/admin/users"))
@dataclass
class UserManagement:
    """User management panel for /admin/users location."""

    auth: Inject[AuthService]

    def __call__(self) -> Node:
        return html(t"<div>User Management</div>")


@injectable(location=PurePath("/"))
@dataclass
class HomePage:
    """Home page for / location."""

    content: Inject[ContentService]

    def __call__(self) -> Node:
        page_content = self.content.get_page_content("/")
        return html(t"<div>Home: {page_content}</div>")
