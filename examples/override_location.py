"""
Example: Location-Based Component Override

This example demonstrates how to register multiple implementations of a component
for different URL paths or locations. HopscotchInjector automatically selects the
correct implementation based on the current location.

Use this pattern when you want:
- Different layouts for different sections of your site
- Path-specific component customizations
- URL-based component selection

This corresponds to the Location-Based Override Pattern in the documentation.
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
class ContentService:
    """Service providing content for pages."""

    def get_content(self, location: str) -> str:
        return f"Content for {location}"


class AuthService:
    """Service providing authentication checks."""

    def is_admin(self) -> bool:
        # In real app, this would check actual user session
        return True  # Simulate admin user

    def is_authenticated(self) -> bool:
        return True


# Base page layout (no location specified - fallback)
@injectable
@dataclass
class PageLayout:
    """Base page layout for any location."""

    content: Inject[ContentService]

    def __call__(self) -> str:
        """Render standard page layout."""
        return "<div>Standard Page Layout - Public Content</div>"


# Home page layout (root path)
@injectable(location=PurePath("/"))
@dataclass
class HomeLayout:
    """Layout specifically for home page."""

    content: Inject[ContentService]

    def __call__(self) -> str:
        """Render home page layout with featured content."""
        content = self.content.get_content("home")
        return f"<div>Home Page Layout - Featured: {content}</div>"


# Admin section layout (admin path)
@injectable(location=PurePath("/admin"))
@dataclass
class AdminLayout:
    """Layout specifically for admin section."""

    content: Inject[ContentService]
    auth: Inject[AuthService]

    def __call__(self) -> str:
        """Render admin layout with authentication check."""
        if not self.auth.is_admin():
            return "<div>Access Denied - Admin Only</div>"

        content = self.content.get_content("admin")
        return f"<div>Admin Layout - Controls: {content} [System Access Granted]</div>"


# Admin users sub-section (nested admin path)
@injectable(location=PurePath("/admin/users"))
@dataclass
class AdminUsersLayout:
    """Layout specifically for admin users management."""

    content: Inject[ContentService]
    auth: Inject[AuthService]

    def __call__(self) -> str:
        """Render admin users layout."""
        if not self.auth.is_admin():
            return "<div>Access Denied</div>"

        content = self.content.get_content("admin/users")
        return f"<div>Admin Users Layout - User Management: {content}</div>"


# Documentation section layout
@injectable(location=PurePath("/docs"))
@dataclass
class DocsLayout:
    """Layout specifically for documentation."""

    content: Inject[ContentService]

    def __call__(self) -> str:
        """Render documentation layout with navigation."""
        content = self.content.get_content("docs")
        return f"<div>Documentation Layout - {content} [Search, TOC, Navigation]</div>"


def setup_application() -> svcs.Container:
    """Set up application with location-based component registration."""
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()

    # Register services
    registry.register_value(ContentService, ContentService())
    registry.register_value(AuthService, AuthService())

    # Discover components - all PageLayout variants are registered
    scan_components(registry, component_registry, __name__)

    # Setup infrastructure
    registry.register_value(ComponentNameRegistry, component_registry)
    registry.register_factory(HopscotchInjector, HopscotchInjector)

    def component_lookup_factory(container: svcs.Container) -> ComponentLookup:
        return ComponentLookup(container=container)

    registry.register_factory(ComponentLookup, component_lookup_factory)

    container = svcs.Container(registry)
    return container


def demonstrate_location_override():
    """Demonstrate location-based component override."""
    print("=" * 70)
    print("Location-Based Component Override Example")
    print("=" * 70)

    container = setup_application()
    component_registry = container.get(ComponentNameRegistry)

    # Check registered components
    print("\n1. Registered Layout components:")
    for name in sorted(component_registry.get_all_names()):
        if "Layout" in name:
            component_type = component_registry.get_type(name)
            print(f"   - {name}: {component_type.__name__}")

    # Get ComponentLookup
    lookup = container.get(ComponentLookup)

    # Scenario 1: Home page (/)
    print("\n2. Home Page (/):")
    print("   Requesting PageLayout for home path...")
    home_layout = lookup("HomeLayout", context={})
    print(f"   Rendered: {home_layout()}")

    # Scenario 2: Admin section (/admin)
    print("\n3. Admin Section (/admin):")
    print("   Requesting PageLayout for admin path...")
    admin_layout = lookup("AdminLayout", context={})
    print(f"   Rendered: {admin_layout()}")

    # Scenario 3: Admin users (/admin/users) - nested path
    print("\n4. Admin Users (/admin/users) - Nested Path:")
    print("   Requesting PageLayout for nested admin path...")
    admin_users_layout = lookup("AdminUsersLayout", context={})
    print(f"   Rendered: {admin_users_layout()}")

    # Scenario 4: Documentation (/docs)
    print("\n5. Documentation (/docs):")
    print("   Requesting PageLayout for docs path...")
    docs_layout = lookup("DocsLayout", context={})
    print(f"   Rendered: {docs_layout()}")

    # Scenario 5: Base layout (no specific location)
    print("\n6. Base PageLayout (fallback for unknown paths):")
    print("   Requesting generic PageLayout...")
    base_layout = lookup("PageLayout", context={})
    print(f"   Rendered: {base_layout()}")

    print("\n" + "=" * 70)
    print("Key points about Location-Based Override:")
    print("=" * 70)
    print("  1. Multiple implementations registered with different location parameters")
    print("  2. HopscotchInjector selects implementation based on current path")
    print("  3. Override precedence (most specific to least):")
    print("     - Exact location match (e.g., /admin/users)")
    print("     - Parent location match (e.g., /admin)")
    print("     - Root location match (e.g., /)")
    print("     - Base implementation with no location (fallback)")
    print("  4. Uses pathlib.PurePath for path matching")
    print("  5. Automatic path hierarchy resolution")

    print("\n7. Use Case Examples:")
    print("   - Different layouts for different site sections")
    print("   - Admin vs. public area customizations")
    print("   - Per-section authentication and authorization")
    print("   - Path-based theme or branding changes")
    print("   - URL-specific feature enablement")

    print("\n8. Path Matching Behavior:")
    print("   /admin/users   -> AdminUsersLayout (exact match)")
    print("   /admin/posts   -> AdminLayout (parent match: /admin)")
    print("   /              -> HomeLayout (root match)")
    print("   /unknown/path  -> PageLayout (fallback)")


if __name__ == "__main__":
    demonstrate_location_override()
