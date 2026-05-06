"""Example: Using categories with decorator and imperative approaches.

This example demonstrates:
- Using @middleware and @hookable decorators with additional categories
- Imperative registration with register_middleware() and register_hookable()
- Querying role groups by kind and user facets by category
- Building organizational structures with categories
"""

from dataclasses import dataclass
from typing import Any, cast

from svcs_hopscotch.injectors import HopscotchContainer, HopscotchRegistry

from tdom_svcs import (
    Middleware,
    Props,
    PropsResult,
    Target,
    hookable,
    middleware,
    register_hookable,
    register_middleware,
    scan,
)

# =============================================================================
# Decorator Approach
# =============================================================================


# docs: start decorator-middleware
@middleware(categories=["security", "auth"])
@dataclass
class AuthenticationMiddleware:
    """Middleware for authentication - tagged as security and auth."""

    priority: int = -20

    def __call__(self, target, props, context):
        props["authenticated"] = True
        return props


@middleware(categories=["security", "validation"])
@dataclass
class ValidationMiddleware:
    """Middleware for validation - tagged as security and validation."""

    priority: int = -10

    def __call__(self, target, props, context):
        props["validated"] = True
        return props


# docs: end decorator-middleware


# docs: start decorator-hookables
@hookable(categories=["page", "admin"])
@dataclass
class AdminDashboard:
    """Admin dashboard page - tagged as page and admin."""

    title: str = "Admin Dashboard"


@hookable(categories=["widget", "interactive"])
@dataclass
class Button:
    """Interactive button widget - tagged as widget and interactive."""

    label: str = "Click me"


# docs: end decorator-hookables

# =============================================================================
# Imperative Approach
# =============================================================================


# docs: start imperative-middleware
@dataclass
class AuditMiddleware(Middleware):
    """Middleware for audit logging - registered imperatively."""

    priority: int = 0

    def __call__(self, target: Target, props: Props, context: Any) -> PropsResult:
        props["audited"] = True
        return props


# docs: end imperative-middleware


# docs: start imperative-hookable
@dataclass
class PublicPage:
    """A public page - registered imperatively."""

    title: str = "Public Area"


# docs: end imperative-hookable

# =============================================================================
# Main Example
# =============================================================================


def main() -> list[str]:
    """Demonstrate kind-based role discovery and category facets."""
    registry = HopscotchRegistry()
    results = []

    # docs: start scan-and-register
    # Scan decorated classes
    scan(registry, locals_dict=globals())

    # Register additional items imperatively
    register_middleware(registry, AuditMiddleware, categories=["audit", "compliance"])
    register_hookable(registry, PublicPage, categories=["page", "public"])
    # docs: end scan-and-register

    # docs: start category-queries
    # List all categories
    # docs: start category-listing
    all_categories = sorted(registry.list_categories())
    results.append(f"All categories: {all_categories}")
    # docs: end category-listing

    # Query middleware by role kind
    all_middleware = list(registry.get_by_kind("middleware"))
    results.append(f"Total middleware: {len(all_middleware)}")

    # docs: start category-facet-query
    security_middleware = [
        cast(type[Middleware], mw_type)
        for mw_type in registry.get_by_category("security")
    ]
    results.append(f"Security middleware: {[m.__name__ for m in security_middleware]}")
    # docs: end category-facet-query

    # Query hookables by role kind
    all_hookables = list(registry.get_by_kind("hookable"))
    results.append(f"Total hookables: {len(all_hookables)}")

    page_items = [cast(type, item) for item in registry.get_by_category("page")]
    results.append(f"Page items: {[c.__name__ for c in page_items]}")

    # Check specific item categories
    # docs: start item-category-query
    auth_categories = sorted(registry.get_categories(AuthenticationMiddleware))
    results.append(f"AuthenticationMiddleware categories: {auth_categories}")
    # docs: end item-category-query
    # docs: end category-queries

    # docs: start middleware-execution
    # Execute security middleware example
    with HopscotchContainer(registry) as container:
        security_middleware = [
            cast(type[Middleware], mw_type)
            for mw_type in registry.get_by_category("security")
        ]
        props: dict[str, object] = {"component": "TestComponent"}

        resolved = [container.get(mw_type) for mw_type in security_middleware]
        resolved.sort(key=lambda m: m.priority)
        for mw in resolved:
            result = mw(Button, props, container)
            if result is not None:
                props = result

        results.append(
            f"Security execution: authenticated={props.get('authenticated')}, "
            f"validated={props.get('validated')}"
        )
    # docs: end middleware-execution

    return results


if __name__ == "__main__":
    results = main()
    print("=" * 70)
    print("Categories Example (Decorator + Imperative)")
    print("=" * 70)
    for result in results:
        print(f"  {result}")
    print("=" * 70)
