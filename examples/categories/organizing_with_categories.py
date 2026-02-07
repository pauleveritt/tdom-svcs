"""Example: Organizing middleware and components with additional categories.

This example demonstrates how to use additional categories to organize and
filter middleware and components. Categories enable you to:

- Tag items for organizational purposes
- Query subsets of middleware/components by category
- Build dynamic menus or configuration based on categories
- Separate concerns (e.g., "security", "logging", "analytics")
"""

from dataclasses import dataclass

from svcs_di.injectors import HopscotchContainer, HopscotchRegistry

from tdom_svcs import component, middleware, scan


# =============================================================================
# Middleware with Categories
# =============================================================================


@middleware(categories=["security", "auth"])
@dataclass
class AuthenticationMiddleware:
    """Middleware for authentication - tagged as security and auth."""

    priority: int = -20

    def __call__(self, component, props, context):
        print("  [Auth] Checking authentication")
        props["authenticated"] = True
        return props


@middleware(categories=["security", "validation"])
@dataclass
class ValidationMiddleware:
    """Middleware for validation - tagged as security and validation."""

    priority: int = -10

    def __call__(self, component, props, context):
        print("  [Validation] Validating props")
        props["validated"] = True
        return props


@middleware(categories=["logging", "analytics"])
@dataclass
class LoggingMiddleware:
    """Middleware for logging - tagged as logging and analytics."""

    priority: int = 0

    def __call__(self, component, props, context):
        print(f"  [Logging] Processing {component.__name__}")
        props["logged"] = True
        return props


# =============================================================================
# Components with Categories
# =============================================================================


@component(categories=["page", "admin"])
@dataclass
class AdminDashboard:
    """Admin dashboard page - tagged as page and admin."""

    title: str = "Admin Dashboard"


@component(categories=["page", "public"])
@dataclass
class HomePage:
    """Public home page - tagged as page and public."""

    title: str = "Welcome"


@component(categories=["widget", "interactive"])
@dataclass
class Button:
    """Interactive button widget - tagged as widget and interactive."""

    label: str = "Click me"


@component(categories=["widget", "display"])
@dataclass
class Label:
    """Display-only label widget - tagged as widget and display."""

    text: str = "Hello"


# =============================================================================
# Using Categories
# =============================================================================


def main():
    """Demonstrate category-based organization and querying."""
    registry = HopscotchRegistry()

    # Scan all decorated classes from this module
    import __main__

    scan(registry, __main__)

    print("=" * 70)
    print("Category-Based Organization Example")
    print("=" * 70)

    # List all categories
    all_categories = registry.list_categories()
    print(f"\nAll categories in registry: {sorted(all_categories)}")

    # Query middleware by category
    print("\n--- Middleware by Category ---")

    print("\n1. All middleware:")
    for mw in registry.get_by_category("middleware"):
        print(f"   - {mw.__name__}")

    print("\n2. Security-related middleware:")
    for mw in registry.get_by_category("security"):
        print(f"   - {mw.__name__}")

    print("\n3. Logging-related middleware:")
    for mw in registry.get_by_category("logging"):
        print(f"   - {mw.__name__}")

    # Query components by category
    print("\n--- Components by Category ---")

    print("\n1. All components:")
    for comp in registry.get_by_category("component"):
        print(f"   - {comp.__name__}")

    print("\n2. Page components:")
    for comp in registry.get_by_category("page"):
        print(f"   - {comp.__name__}")

    print("\n3. Widget components:")
    for comp in registry.get_by_category("widget"):
        print(f"   - {comp.__name__}")

    print("\n4. Interactive components:")
    for comp in registry.get_by_category("interactive"):
        print(f"   - {comp.__name__}")

    # Check categories for specific items
    print("\n--- Categories for Specific Items ---")

    print("\nAuthenticationMiddleware categories:")
    auth_categories = registry.get_categories(AuthenticationMiddleware)
    print(f"   {sorted(auth_categories)}")

    print("\nButton component categories:")
    button_categories = registry.get_categories(Button)
    print(f"   {sorted(button_categories)}")

    # Demonstrate execution with filtered middleware
    print("\n--- Executing with Filtered Middleware ---")

    with HopscotchContainer(registry) as container:
        # Execute only security middleware
        print("\nExecuting security middleware only:")
        security_middleware = list(registry.get_by_category("security"))

        props = {"component": "TestComponent"}
        # Resolve from container and sort by priority
        resolved = [container.get(mw_type) for mw_type in security_middleware]
        resolved.sort(key=lambda m: m.priority)
        for mw in resolved:
            props = mw(Button, props, container)

        print(f"   Result: {props}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
