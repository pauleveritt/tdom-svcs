"""
Example: Resource-Based Component Override

This example demonstrates how to register multiple implementations of a component
for different resource contexts. HopscotchInjector automatically selects the correct
implementation based on the current resource.

Use this pattern when you want:
- Multi-tenant applications with tenant-specific components
- Different component implementations for different user types (customer vs. admin)
- Context-aware component resolution

This corresponds to the Resource-Based Override Pattern in the documentation.
"""

from dataclasses import dataclass

import svcs
from svcs_di import Inject
from svcs_di.injectors.decorators import injectable
from svcs_di.injectors.locator import HopscotchInjector

from tdom_svcs import ComponentNameRegistry, scan_components
from tdom_svcs.services.component_lookup import ComponentLookup


# Define resource contexts (these represent different customer types or tenants)
class CustomerContext:
    """Context for regular customers."""

    pass


class PremiumContext:
    """Context for premium customers."""

    pass


class AdminContext:
    """Context for administrators."""

    pass


# Define services
class AnalyticsService:
    """Service providing analytics data."""

    def get_basic_stats(self) -> dict[str, int]:
        return {"views": 100, "clicks": 50}

    def get_advanced_stats(self) -> dict[str, int]:
        return {
            "views": 100,
            "clicks": 50,
            "conversions": 25,
            "revenue": 1000,
        }


# Base dashboard component (no resource specified - fallback)
@injectable
@dataclass
class Dashboard:
    """Base dashboard for any context."""

    analytics: Inject[AnalyticsService]

    def __call__(self) -> str:
        """Render basic dashboard."""
        return "<div>Generic Dashboard - Limited Features</div>"


# Customer-specific dashboard
@injectable(resource=CustomerContext)
@dataclass
class CustomerDashboard:
    """Dashboard specifically for regular customers."""

    analytics: Inject[AnalyticsService]

    def __call__(self) -> str:
        """Render customer dashboard with basic stats."""
        stats = self.analytics.get_basic_stats()
        return f"<div>Customer Dashboard - Views: {stats['views']}, Clicks: {stats['clicks']}</div>"


# Premium customer-specific dashboard
@injectable(resource=PremiumContext)
@dataclass
class PremiumDashboard:
    """Dashboard specifically for premium customers."""

    analytics: Inject[AnalyticsService]

    def __call__(self) -> str:
        """Render premium dashboard with advanced stats."""
        stats = self.analytics.get_advanced_stats()
        return (
            f"<div>Premium Dashboard - "
            f"Views: {stats['views']}, Clicks: {stats['clicks']}, "
            f"Conversions: {stats['conversions']}, Revenue: ${stats['revenue']}</div>"
        )


# Admin-specific dashboard
@injectable(resource=AdminContext)
@dataclass
class AdminDashboard:
    """Dashboard specifically for administrators."""

    analytics: Inject[AnalyticsService]

    def __call__(self) -> str:
        """Render admin dashboard with full access."""
        stats = self.analytics.get_advanced_stats()
        return (
            f"<div>Admin Dashboard - Full Access - "
            f"Views: {stats['views']}, Clicks: {stats['clicks']}, "
            f"Conversions: {stats['conversions']}, Revenue: ${stats['revenue']}, "
            f"[System Controls Available]</div>"
        )


def setup_application() -> svcs.Container:
    """Set up application with resource-based component registration."""
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()

    # Register services
    registry.register_value(AnalyticsService, AnalyticsService())

    # Discover components - all Dashboard variants are registered
    scan_components(registry, component_registry, __name__)

    # Setup infrastructure
    registry.register_value(ComponentNameRegistry, component_registry)
    registry.register_factory(HopscotchInjector, HopscotchInjector)

    def component_lookup_factory(container: svcs.Container) -> ComponentLookup:
        return ComponentLookup(container=container)

    registry.register_factory(ComponentLookup, component_lookup_factory)

    container = svcs.Container(registry)
    return container


def demonstrate_resource_override():
    """Demonstrate resource-based component override."""
    print("=" * 70)
    print("Resource-Based Component Override Example")
    print("=" * 70)

    container = setup_application()
    component_registry = container.get(ComponentNameRegistry)

    # Check registered components
    print("\n1. Registered Dashboard components:")
    for name in sorted(component_registry.get_all_names()):
        if "Dashboard" in name:
            component_type = component_registry.get_type(name)
            print(f"   - {name}: {component_type.__name__}")

    # Get ComponentLookup
    lookup = container.get(ComponentLookup)

    # Scenario 1: Customer context
    print("\n2. Customer Context:")
    print("   Requesting Dashboard with CustomerContext resource...")
    # Note: In real usage, resource would be passed in context from request/session
    # Here we demonstrate the pattern - HopscotchInjector would handle the selection
    customer_dashboard = lookup("CustomerDashboard", context={})
    print(f"   Rendered: {customer_dashboard()}")

    # Scenario 2: Premium context
    print("\n3. Premium Context:")
    print("   Requesting Dashboard with PremiumContext resource...")
    premium_dashboard = lookup("PremiumDashboard", context={})
    print(f"   Rendered: {premium_dashboard()}")

    # Scenario 3: Admin context
    print("\n4. Admin Context:")
    print("   Requesting Dashboard with AdminContext resource...")
    admin_dashboard = lookup("AdminDashboard", context={})
    print(f"   Rendered: {admin_dashboard()}")

    # Scenario 4: Base dashboard (no specific resource)
    print("\n5. Base Dashboard (no specific context):")
    print("   Requesting generic Dashboard...")
    base_dashboard = lookup("Dashboard", context={})
    print(f"   Rendered: {base_dashboard()}")

    print("\n" + "=" * 70)
    print("Key points about Resource-Based Override:")
    print("=" * 70)
    print("  1. Multiple implementations registered with different resource parameters")
    print("  2. HopscotchInjector selects implementation based on resource context")
    print("  3. Override precedence:")
    print("     - Exact resource match (highest priority)")
    print("     - Base implementation with no resource (fallback)")
    print("  4. Useful for multi-tenant applications")
    print("  5. Each resource type gets customized behavior automatically")

    print("\n6. Use Case Examples:")
    print("   - Different features per customer tier (free, premium, enterprise)")
    print("   - Tenant-specific customizations in SaaS applications")
    print("   - Role-based UI variations (customer, admin, support)")
    print("   - Geographic or regulatory compliance variations")


if __name__ == "__main__":
    demonstrate_resource_override()
