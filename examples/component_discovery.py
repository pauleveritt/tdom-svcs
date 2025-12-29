"""
Example: Component Discovery and Registration

This example demonstrates the complete workflow for using @injectable
decorator and scan_components() to automatically discover and register
components for use with tdom templates.

The workflow involves:
1. Decorating component classes with @injectable
2. Calling scan_components() at application startup
3. Components are automatically discovered and registered in both registries
4. Components can be resolved by string name via ComponentLookup
5. Dependencies are automatically injected via Inject[] type hints
"""

from dataclasses import dataclass

import svcs
from svcs_di import Inject
from svcs_di.injectors.decorators import injectable
from svcs_di.injectors.locator import HopscotchInjector

from tdom_svcs import ComponentNameRegistry, scan_components
from tdom_svcs.services.component_lookup import ComponentLookup


# Step 1: Define service classes for dependency injection
class DatabaseService:
    """Example database service."""

    def get_user(self, user_id: int) -> dict:
        return {"id": user_id, "name": "Alice", "role": "admin"}


class AuthService:
    """Example authentication service."""

    def is_authenticated(self) -> bool:
        return True


# Step 2: Decorate component classes with @injectable
@injectable
@dataclass
class Button:
    """
    Simple button component with no dependencies.

    This component will be automatically discovered by scan_components()
    and registered as "Button" (derived from class.__name__).
    """

    label: str = "Click me"
    disabled: bool = False

    def __call__(self) -> str:
        """Render the button as HTML."""
        disabled_attr = " disabled" if self.disabled else ""
        return f"<button{disabled_attr}>{self.label}</button>"


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
        """Render the admin panel if authenticated."""
        if not self.auth.is_authenticated():
            return "<div>Access Denied</div>"

        return f"""
        <div class="admin-panel">
            <h1>{self.title}</h1>
            <p>Welcome, authenticated admin!</p>
        </div>
        """.strip()


# Step 3: Application startup - setup and scanning
def setup_application():
    """
    Setup application with component discovery.

    This function demonstrates the complete setup workflow:
    1. Create svcs.Registry and ComponentNameRegistry
    2. Register services that components depend on
    3. Scan packages for @injectable components
    4. Setup container with required services
    5. Create ComponentLookup for component resolution
    """
    # Create registries
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()

    # Register services that components will inject
    db_service = DatabaseService()
    auth_service = AuthService()
    registry.register_value(DatabaseService, db_service)
    registry.register_value(AuthService, auth_service)

    # Scan this module for @injectable decorated components
    # In a real app, you'd specify your component packages:
    # scan_components(registry, component_registry, "myapp.components", "myapp.widgets")
    scan_components(registry, component_registry, __name__)

    # Create container
    container = svcs.Container(registry)

    # Setup ComponentNameRegistry and injector in container
    registry.register_value(ComponentNameRegistry, component_registry)
    registry.register_factory(HopscotchInjector, HopscotchInjector)

    # Create ComponentLookup for resolving components
    lookup = ComponentLookup(container=container)

    return lookup, component_registry


# Step 4: Using components after setup
def demonstrate_component_usage():
    """Demonstrate using components after setup."""
    # Setup application
    lookup, component_registry = setup_application()

    print("Component Discovery Example")
    print("=" * 50)

    # Check what components were discovered
    print("\nDiscovered components:")
    for name in sorted(component_registry.get_all_names()):
        print(f"  - {name}")

    print("\n" + "=" * 50)

    # Resolve and use Button component (no dependencies)
    print("\n1. Simple Button component (no dependencies):")
    context = {}
    button = lookup("Button", context)
    if button:
        print(f"   Rendered: {button()}")

    # Resolve and use UserProfile component (with injected dependencies)
    print("\n2. UserProfile component (with Inject[DatabaseService]):")
    user_profile = lookup("UserProfile", context)
    if user_profile:
        # Note: user_id has a default value, db is injected
        rendered = user_profile()
        print(f"   Rendered: {rendered}")

    # Resolve and use AdminPanel component (multiple injected dependencies)
    print("\n3. AdminPanel component (multiple injected dependencies):")
    admin_panel = lookup("AdminPanel", context)
    if admin_panel:
        rendered = admin_panel()
        print(f"   Rendered: {rendered}")

    print("\n" + "=" * 50)

    # Demonstrate error handling - component not found
    print("\n4. Error handling - component not found:")
    try:
        lookup("NonExistentComponent", context)
    except Exception as e:
        print(f"   Error: {type(e).__name__}: {e}")

    print("\n" + "=" * 50)
    print("\nKey takeaways:")
    print("  1. @injectable decorator marks components for discovery")
    print("  2. scan_components() finds and registers all decorated components")
    print("  3. Components are registered by class.__name__ (e.g., 'Button')")
    print("  4. Inject[T] parameters are resolved from svcs container")
    print("  5. Regular parameters can have defaults or be passed as props")
    print("  6. Two-stage resolution: name->type->instance")


if __name__ == "__main__":
    demonstrate_component_usage()
