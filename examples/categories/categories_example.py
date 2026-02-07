"""Example: Using categories with decorator and imperative approaches.

This example demonstrates:
- Using @middleware and @component decorators with additional categories
- Imperative registration with register_middleware() and register_component()
- Querying items by category
- Building organizational structures with categories
"""

from dataclasses import dataclass

from svcs_di.injectors import HopscotchContainer, HopscotchRegistry

from tdom_svcs import component, middleware, register_middleware, scan
from tdom_svcs.services.middleware import register_component


# =============================================================================
# Decorator Approach
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


@component(categories=["page", "admin"])
@dataclass
class AdminDashboard:
    """Admin dashboard page - tagged as page and admin."""

    title: str = "Admin Dashboard"


@component(categories=["widget", "interactive"])
@dataclass
class Button:
    """Interactive button widget - tagged as widget and interactive."""

    label: str = "Click me"


# =============================================================================
# Imperative Approach
# =============================================================================


@dataclass
class AuditMiddleware:
    """Middleware for audit logging - registered imperatively."""

    priority: int = 0

    def __call__(self, component, props, context):
        props["audited"] = True
        return props


@dataclass
class PublicPage:
    """A public page component - registered imperatively."""

    title: str = "Public Area"


# =============================================================================
# Main Example
# =============================================================================


def main() -> list[str]:
    """Demonstrate both decorator and imperative category usage."""
    registry = HopscotchRegistry()
    results = []

    # Scan decorated classes
    scan(registry, locals_dict=globals())

    # Register additional items imperatively
    register_middleware(registry, AuditMiddleware, categories=["audit", "compliance"])
    register_component(registry, PublicPage, categories=["page", "public"])

    # List all categories
    all_categories = sorted(registry.list_categories())
    results.append(f"All categories: {all_categories}")

    # Query middleware
    all_middleware = list(registry.get_by_category("middleware"))
    results.append(f"Total middleware: {len(all_middleware)}")

    security_middleware = list(registry.get_by_category("security"))
    results.append(f"Security middleware: {[m.__name__ for m in security_middleware]}")

    # Query components
    all_components = list(registry.get_by_category("component"))
    results.append(f"Total components: {len(all_components)}")

    page_components = list(registry.get_by_category("page"))
    results.append(f"Page components: {[c.__name__ for c in page_components]}")

    # Check specific item categories
    auth_categories = sorted(registry.get_categories(AuthenticationMiddleware))
    results.append(f"AuthenticationMiddleware categories: {auth_categories}")

    # Execute security middleware example
    with HopscotchContainer(registry) as container:
        security_middleware = list(registry.get_by_category("security"))
        props: dict[str, object] = {"component": "TestComponent"}

        resolved = [container.get(mw_type) for mw_type in security_middleware]
        resolved.sort(key=lambda m: m.priority)
        for mw in resolved:
            result = mw(Button, props, container)  # ty: ignore[call-non-callable]
            if result is not None:
                props = result

        results.append(
            f"Security execution: authenticated={props.get('authenticated')}, "
            f"validated={props.get('validated')}"
        )

    return results


if __name__ == "__main__":
    results = main()
    print("=" * 70)
    print("Categories Example (Decorator + Imperative)")
    print("=" * 70)
    for result in results:
        print(f"  {result}")
    print("=" * 70)
