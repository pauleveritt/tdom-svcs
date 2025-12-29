"""
Example: Location-Based Component Registration

This example demonstrates how to use @injectable with location-based registration.
Components can be registered for specific URL paths or locations, allowing
route-specific component resolution.

This corresponds to Example 3 in spec.md (line 137).
"""

from dataclasses import dataclass
from pathlib import PurePath

import svcs
from svcs_di import Inject
from svcs_di.injectors.decorators import injectable
from svcs_di.injectors.locator import HopscotchInjector

from tdom_svcs import ComponentNameRegistry, scan_components
from tdom_svcs.services.component_lookup import ComponentLookup


# Define services
class AuthService:
    """Service for authentication."""

    def is_admin(self) -> bool:
        return True  # Simplified for example

    def get_current_user(self) -> str:
        return "admin@example.com"


class ContentService:
    """Service for content management."""

    def get_page_content(self, path: str) -> str:
        return f"Content for {path}"


# Define components with location-based registration
@injectable(location=PurePath("/admin"))
@dataclass
class AdminPanel:
    """
    Admin panel component for /admin routes.

    This component is registered with /admin as the location,
    meaning it's intended for admin routes only.
    """

    auth: Inject[AuthService]

    def __call__(self) -> str:
        """Render admin panel."""
        if not self.auth.is_admin():
            return "<div>Access Denied</div>"

        user = self.auth.get_current_user()
        return f"""
        <div class="admin-panel">
            <h1>Admin Panel</h1>
            <p>Logged in as: {user}</p>
            <nav>
                <a href="/admin/users">Users</a> |
                <a href="/admin/settings">Settings</a> |
                <a href="/admin/logs">Logs</a>
            </nav>
        </div>
        """.strip()


@injectable(location=PurePath("/admin/users"))
@dataclass
class UserManagement:
    """
    User management component for /admin/users route.

    This is a more specific location than /admin, showing
    nested route handling.
    """

    auth: Inject[AuthService]

    def __call__(self) -> str:
        """Render user management."""
        return """
        <div class="user-management">
            <h2>User Management</h2>
            <table>
                <tr><th>Email</th><th>Role</th><th>Actions</th></tr>
                <tr><td>admin@example.com</td><td>Admin</td><td>Edit | Delete</td></tr>
                <tr><td>user@example.com</td><td>User</td><td>Edit | Delete</td></tr>
            </table>
        </div>
        """.strip()


@injectable(location=PurePath("/"))
@dataclass
class HomePage:
    """
    Home page component for root route.

    This demonstrates location-based registration for the root path.
    """

    content: Inject[ContentService]

    def __call__(self) -> str:
        """Render home page."""
        page_content = self.content.get_page_content("/")
        return f"""
        <div class="home-page">
            <h1>Welcome Home</h1>
            <p>{page_content}</p>
        </div>
        """.strip()


def setup_application():
    """Setup application with location-based components."""
    # Create registries
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()

    # Register services
    auth_service = AuthService()
    content_service = ContentService()
    registry.register_value(AuthService, auth_service)
    registry.register_value(ContentService, content_service)

    # Scan this module for @injectable components
    scan_components(registry, component_registry, __name__)

    # Setup container
    container = svcs.Container(registry)
    registry.register_value(ComponentNameRegistry, component_registry)
    registry.register_factory(HopscotchInjector, HopscotchInjector)

    # Create ComponentLookup
    lookup = ComponentLookup(container=container)

    return lookup, component_registry


def demonstrate_location_based_components():
    """Demonstrate location-based component resolution."""
    lookup, component_registry = setup_application()

    print("Location-Based Components Example")
    print("=" * 60)

    # Check what components were discovered
    print("\nDiscovered components:")
    for name in sorted(component_registry.get_all_names()):
        print(f"  - {name}")

    print("\n" + "=" * 60)

    # Resolve components for different routes
    context = {}

    print("\n1. Admin Panel (location=/admin):")
    admin_panel = lookup("AdminPanel", context)
    if admin_panel:
        rendered = admin_panel()
        print(f"   {rendered}")

    print("\n2. User Management (location=/admin/users):")
    user_mgmt = lookup("UserManagement", context)
    if user_mgmt:
        rendered = user_mgmt()
        print(f"   {rendered}")

    print("\n3. Home Page (location=/):")
    home_page = lookup("HomePage", context)
    if home_page:
        rendered = home_page()
        print(f"   {rendered}")

    print("\n" + "=" * 60)
    print("\nKey points:")
    print("  1. Components can be registered with location metadata")
    print("  2. @injectable(location=PurePath(...)) associates with routes")
    print("  3. Components are still discoverable by string name")
    print("  4. Location metadata is handled by svcs-di's scan()")
    print("  5. Useful for route-specific components and layouts")
    print("  6. Supports nested paths (/admin vs /admin/users)")


if __name__ == "__main__":
    demonstrate_location_based_components()
