"""
Example: Resource-Based Component Registration

This example demonstrates how to use @injectable with resource-based registration.
Components can be registered for specific resource contexts, allowing different
components to be resolved based on the current application context.

This corresponds to Example 2 in spec.md (line 118).
"""

from dataclasses import dataclass

import svcs
from svcs_di import Inject
from svcs_di.injectors.decorators import injectable
from svcs_di.injectors.keyword import KeywordInjector

from tdom_svcs import ComponentNameRegistry, scan_components
from tdom_svcs.services.component_lookup import ComponentLookup


# Define resource types for context
class CustomerContext:
    """Context for customer-facing views."""

    pass


class AdminContext:
    """Context for admin views."""

    pass


# Define services
class UserService:
    """Service for user operations."""

    def get_current_user(self) -> dict:
        return {"name": "Alice", "role": "customer"}


class AnalyticsService:
    """Service for analytics."""

    def get_stats(self) -> dict:
        return {"visits": 1000, "conversions": 50}


# Define components with resource-based registration
@injectable(resource=CustomerContext)
@dataclass
class CustomerDashboard:
    """
    Dashboard shown only for customer context.

    This component is registered with CustomerContext as the resource,
    meaning it can be resolved differently based on the context.
    """

    user: Inject[UserService] = None
    analytics: Inject[AnalyticsService] = None

    def __call__(self) -> str:
        """Render customer dashboard."""
        user = self.user.get_current_user()
        stats = self.analytics.get_stats()
        return f"""
        <div class="customer-dashboard">
            <h1>Welcome, {user['name']}!</h1>
            <p>You have {stats['visits']} visits</p>
        </div>
        """.strip()


@injectable(resource=AdminContext)
@dataclass
class AdminDashboard:
    """
    Dashboard shown only for admin context.

    This component is registered with AdminContext as the resource,
    providing different functionality for admins.
    """

    analytics: Inject[AnalyticsService] = None

    def __call__(self) -> str:
        """Render admin dashboard."""
        stats = self.analytics.get_stats()
        return f"""
        <div class="admin-dashboard">
            <h1>Admin Dashboard</h1>
            <p>Total visits: {stats['visits']}</p>
            <p>Conversions: {stats['conversions']}</p>
            <p>Conversion rate: {stats['conversions'] / stats['visits'] * 100:.1f}%</p>
        </div>
        """.strip()


def setup_application():
    """Setup application with resource-based components."""
    # Create registries
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()

    # Register services
    user_service = UserService()
    analytics_service = AnalyticsService()
    registry.register_value(UserService, user_service)
    registry.register_value(AnalyticsService, analytics_service)

    # Scan this module for @injectable components
    scan_components(registry, component_registry, __name__)

    # Setup container
    container = svcs.Container(registry)
    registry.register_value(ComponentNameRegistry, component_registry)
    injector = KeywordInjector(container=container)
    registry.register_value(KeywordInjector, injector)

    # Create ComponentLookup
    lookup = ComponentLookup(container=container)

    return lookup, component_registry


def demonstrate_resource_based_components():
    """Demonstrate resource-based component resolution."""
    lookup, component_registry = setup_application()

    print("Resource-Based Components Example")
    print("=" * 60)

    # Check what components were discovered
    print("\nDiscovered components:")
    for name in sorted(component_registry.get_all_names()):
        print(f"  - {name}")

    print("\n" + "=" * 60)

    # Resolve customer dashboard
    print("\n1. Customer Dashboard (resource=CustomerContext):")
    context = {}
    customer_dashboard = lookup("CustomerDashboard", context)
    if customer_dashboard:
        rendered = customer_dashboard()
        print(f"   {rendered}")

    # Resolve admin dashboard
    print("\n2. Admin Dashboard (resource=AdminContext):")
    admin_dashboard = lookup("AdminDashboard", context)
    if admin_dashboard:
        rendered = admin_dashboard()
        print(f"   {rendered}")

    print("\n" + "=" * 60)
    print("\nKey points:")
    print("  1. Components can be registered with resource metadata")
    print("  2. @injectable(resource=X) associates component with context")
    print("  3. Both components are still discoverable by string name")
    print("  4. Resource metadata is handled by svcs-di's scan()")
    print("  5. Different dashboards for different user contexts")


if __name__ == "__main__":
    demonstrate_resource_based_components()
