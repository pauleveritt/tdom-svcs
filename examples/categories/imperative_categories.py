"""Example: Using categories with imperative registration.

This example shows how to use additional categories when registering
middleware and components imperatively (without decorators).
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
        print(f"  [Security] Checking {component.__name__}")
        props["secure"] = True
        return props


@dataclass
class AuditMiddleware:
    """Middleware for audit logging."""

    priority: int = 0

    def __call__(self, component, props, context):
        print(f"  [Audit] Logging access to {component.__name__}")
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


def main():
    """Demonstrate imperative registration with categories."""
    registry = HopscotchRegistry()

    print("=" * 70)
    print("Imperative Registration with Categories")
    print("=" * 70)

    # Register middleware imperatively with categories
    print("\nRegistering middleware with categories...")
    register_middleware(
        registry, SecurityMiddleware, categories=["security", "compliance"]
    )
    register_middleware(registry, AuditMiddleware, categories=["audit", "compliance"])

    # Register components imperatively with categories
    print("Registering components with categories...")
    register_component(registry, SecurePage, categories=["page", "protected"])
    register_component(registry, PublicPage, categories=["page", "public"])

    # Show registered categories
    print(f"\nAll categories: {sorted(registry.list_categories())}")

    # Query by category
    print("\n--- Query by Category ---")

    print("\n1. Middleware:")
    for mw in registry.get_by_category("middleware"):
        cats = sorted(registry.get_categories(mw))
        print(f"   - {mw.__name__}: {cats}")

    print("\n2. Compliance-related items:")
    for item in registry.get_by_category("compliance"):
        print(f"   - {item.__name__}")

    print("\n3. Page components:")
    for comp in registry.get_by_category("page"):
        cats = sorted(registry.get_categories(comp))
        print(f"   - {comp.__name__}: {cats}")

    print("\n4. Protected components:")
    for comp in registry.get_by_category("protected"):
        print(f"   - {comp.__name__}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
