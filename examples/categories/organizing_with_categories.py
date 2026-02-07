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
        props["authenticated"] = True
        return props


@middleware(categories=["security", "validation"])
@dataclass
class ValidationMiddleware:
    """Middleware for validation - tagged as security and validation."""

    priority: int = -10

    def __call__(self, component, props, context):
        props["validated"] = True
        return props


@middleware(categories=["logging", "analytics"])
@dataclass
class LoggingMiddleware:
    """Middleware for logging - tagged as logging and analytics."""

    priority: int = 0

    def __call__(self, component, props, context):
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


def main() -> list[str]:
    """Demonstrate category-based organization and querying."""
    registry = HopscotchRegistry()
    results = []

    # Scan all decorated classes from this module
    scan(registry, locals_dict=globals())

    # List all categories
    all_categories = sorted(registry.list_categories())
    results.append(f"All categories: {all_categories}")
    assert len(all_categories) >= 8  # middleware, component, security, auth, validation, logging, analytics, page, admin, public, widget, interactive, display

    # Query middleware by category
    all_middleware = list(registry.get_by_category("middleware"))
    results.append(f"All middleware count: {len(all_middleware)}")
    assert len(all_middleware) == 3

    security_middleware = list(registry.get_by_category("security"))
    results.append(f"Security middleware: {[m.__name__ for m in security_middleware]}")
    assert len(security_middleware) == 2

    logging_middleware = list(registry.get_by_category("logging"))
    results.append(f"Logging middleware: {[m.__name__ for m in logging_middleware]}")
    assert len(logging_middleware) == 1

    # Query components by category
    all_components = list(registry.get_by_category("component"))
    results.append(f"All components count: {len(all_components)}")
    assert len(all_components) == 4

    page_components = list(registry.get_by_category("page"))
    results.append(f"Page components: {[c.__name__ for c in page_components]}")
    assert len(page_components) == 2

    widget_components = list(registry.get_by_category("widget"))
    results.append(f"Widget components: {[c.__name__ for c in widget_components]}")
    assert len(widget_components) == 2

    interactive_components = list(registry.get_by_category("interactive"))
    results.append(f"Interactive components: {[c.__name__ for c in interactive_components]}")
    assert len(interactive_components) == 1

    # Check categories for specific items
    auth_categories = sorted(registry.get_categories(AuthenticationMiddleware))
    results.append(f"AuthenticationMiddleware categories: {auth_categories}")
    assert "middleware" in auth_categories
    assert "security" in auth_categories
    assert "auth" in auth_categories

    button_categories = sorted(registry.get_categories(Button))
    results.append(f"Button categories: {button_categories}")
    assert "component" in button_categories
    assert "widget" in button_categories
    assert "interactive" in button_categories

    # Demonstrate execution with filtered middleware
    with HopscotchContainer(registry) as container:
        # Execute only security middleware
        security_middleware = list(registry.get_by_category("security"))
        props = {"component": "TestComponent"}

        # Resolve from container and sort by priority
        resolved = [container.get(mw_type) for mw_type in security_middleware]
        resolved.sort(key=lambda m: m.priority)
        for mw in resolved:
            props = mw(Button, props, container)

        results.append(f"Security middleware execution result: authenticated={props.get('authenticated')}, validated={props.get('validated')}")
        assert props["authenticated"] is True
        assert props["validated"] is True

    return results


if __name__ == "__main__":
    results = main()
    print("=" * 70)
    print("Category-Based Organization Example")
    print("=" * 70)
    for result in results:
        print(f"  {result}")
    print("=" * 70)
