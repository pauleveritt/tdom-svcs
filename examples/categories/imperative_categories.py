"""Example: Using categories with imperative registration.

This example demonstrates:

- Imperative registration with register_middleware() and register_component()
- Adding categories to middleware and components without decorators
- Integrating third-party classes into the category system
- Querying items by category after imperative registration
"""

from dataclasses import dataclass

from svcs_di.injectors import HopscotchRegistry

from tdom_svcs import register_middleware
from tdom_svcs.services.middleware import register_component


# Define middleware and components without decorators
@dataclass
class SecurityMiddleware:
    """Middleware for security checks."""

    priority: int = -10

    def __call__(self, component, props, context):
        props["secure"] = True
        return props


@dataclass
class AuditMiddleware:
    """Middleware for audit logging."""

    priority: int = 0

    def __call__(self, component, props, context):
        props["audited"] = True
        return props


@dataclass
class SecurePage:
    """A secure page component."""

    title: str = "Secure Area"


@dataclass
class PublicPage:
    """A public page component."""

    title: str = "Public Area"


def main() -> list[str]:
    """Demonstrate imperative registration with categories."""
    registry = HopscotchRegistry()
    results = []

    # Register middleware imperatively with categories
    register_middleware(
        registry, SecurityMiddleware, categories=["security", "compliance"]
    )
    register_middleware(registry, AuditMiddleware, categories=["audit", "compliance"])

    # Register components imperatively with categories
    register_component(registry, SecurePage, categories=["page", "protected"])
    register_component(registry, PublicPage, categories=["page", "public"])

    # Show registered categories
    all_categories = sorted(registry.list_categories())
    results.append(f"All categories: {all_categories}")
    assert len(all_categories) >= 7  # middleware, component, security, compliance, audit, page, protected, public

    # Query by category
    all_middleware = list(registry.get_by_category("middleware"))
    results.append(f"Middleware count: {len(all_middleware)}")
    assert len(all_middleware) == 2

    for mw in all_middleware:
        cats = sorted(registry.get_categories(mw))
        results.append(f"  {mw.__name__}: {cats}")
        assert "middleware" in cats

    compliance_items = list(registry.get_by_category("compliance"))
    results.append(f"Compliance items: {[i.__name__ for i in compliance_items]}")
    assert len(compliance_items) == 2

    page_components = list(registry.get_by_category("page"))
    results.append(f"Page components count: {len(page_components)}")
    assert len(page_components) == 2

    for comp in page_components:
        cats = sorted(registry.get_categories(comp))
        results.append(f"  {comp.__name__}: {cats}")
        assert "component" in cats
        assert "page" in cats

    protected_components = list(registry.get_by_category("protected"))
    results.append(f"Protected components: {[c.__name__ for c in protected_components]}")
    assert len(protected_components) == 1
    assert SecurePage in protected_components

    return results


if __name__ == "__main__":
    results = main()
    print("=" * 70)
    print("Imperative Registration with Categories")
    print("=" * 70)
    for result in results:
        print(result)
    print("=" * 70)
