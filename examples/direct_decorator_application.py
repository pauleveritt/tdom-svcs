"""
Example: Direct Decorator Application

This example demonstrates using injectable() directly without decorator syntax.
This is useful for programmatic decoration, conditional registration, and
creating variants of components.

This corresponds to Examples 4 and 5 in spec.md (lines 159 and 180).

Note: When applying injectable() directly, the registered name is still the
original class name. Variants share the same string name but have different
resource metadata.
"""

from dataclasses import dataclass

import svcs
from svcs_di import Inject
from svcs_di.injectors.decorators import injectable
from svcs_di.injectors.keyword import KeywordInjector

from tdom_svcs import ComponentNameRegistry, scan_components
from tdom_svcs.services.component_lookup import ComponentLookup


# Define context types
class CustomerContext:
    """Customer context."""

    pass


class AdminContext:
    """Admin context."""

    pass


# Define services
class ThemeService:
    """Service for theming."""

    def get_theme(self, context_type: str) -> str:
        themes = {
            "customer": "blue",
            "admin": "red",
            "default": "green",
        }
        return themes.get(context_type, "default")


# Example 4: Direct decorator application without decorator syntax
@dataclass
class Card:
    """
    A card component without @injectable decorator.

    We'll apply the decorator programmatically below.
    """

    title: str = "Default Card"
    content: str = "Default content"

    def __call__(self) -> str:
        """Render the card."""
        return f"""
        <div class="card">
            <h3>{self.title}</h3>
            <p>{self.content}</p>
        </div>
        """.strip()


# Apply decorator directly (Example 4 from spec.md)
Card = injectable(Card)


# Example 5: Creating separate component classes with variants
@dataclass
class CustomerDashboard:
    """Dashboard for customer context."""

    title: str = "Customer Dashboard"
    theme: Inject[ThemeService] = None

    def __call__(self) -> str:
        """Render customer dashboard."""
        color = self.theme.get_theme("customer") if self.theme else "blue"
        return f"""
        <div class="dashboard" style="border: 3px solid {color}">
            <h1>{self.title}</h1>
            <p>Customer-specific dashboard content</p>
        </div>
        """.strip()


@dataclass
class AdminDashboard:
    """Dashboard for admin context."""

    title: str = "Admin Dashboard"
    theme: Inject[ThemeService] = None

    def __call__(self) -> str:
        """Render admin dashboard."""
        color = self.theme.get_theme("admin") if self.theme else "red"
        return f"""
        <div class="dashboard" style="border: 3px solid {color}">
            <h1>{self.title}</h1>
            <p>Admin-specific dashboard content</p>
        </div>
        """.strip()


# Apply decorators with resource metadata
CustomerDashboard = injectable(CustomerDashboard, resource=CustomerContext)
AdminDashboard = injectable(AdminDashboard, resource=AdminContext)


# Example: Conditional decoration based on configuration
class FeatureFlags:
    """Feature flag configuration."""

    enable_analytics = True
    enable_reporting = False


@dataclass
class AnalyticsWidget:
    """Analytics widget component."""

    title: str = "Analytics"

    def __call__(self) -> str:
        return "<div>Analytics: 100 visitors today</div>"


@dataclass
class ReportingWidget:
    """Reporting widget component."""

    title: str = "Reports"

    def __call__(self) -> str:
        return "<div>Reports: 5 new reports</div>"


# Conditionally apply decorator based on feature flags
flags = FeatureFlags()

if flags.enable_analytics:
    AnalyticsWidget = injectable(AnalyticsWidget)

if flags.enable_reporting:
    ReportingWidget = injectable(ReportingWidget)


def setup_application():
    """Setup application with programmatically decorated components."""
    # Create registries
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()

    # Register services
    theme_service = ThemeService()
    registry.register_value(ThemeService, theme_service)

    # Scan this module for @injectable components
    # This will find Card, CustomerDashboard, AdminDashboard, and AnalyticsWidget
    scan_components(registry, component_registry, __name__)

    # Setup container
    container = svcs.Container(registry)
    registry.register_value(ComponentNameRegistry, component_registry)
    injector = KeywordInjector(container=container)
    registry.register_value(KeywordInjector, injector)

    # Create ComponentLookup
    lookup = ComponentLookup(container=container)

    return lookup, component_registry


def demonstrate_direct_decorator_application():
    """Demonstrate direct decorator application patterns."""
    lookup, component_registry = setup_application()

    print("Direct Decorator Application Example")
    print("=" * 60)

    # Check what components were discovered
    print("\nDiscovered components:")
    for name in sorted(component_registry.get_all_names()):
        print(f"  - {name}")

    print("\n" + "=" * 60)

    context = {}

    # Example 4: Basic direct application
    print("\n1. Card (applied with injectable(Card)):")
    card = lookup("Card", context)
    if card:
        rendered = card()
        print(f"   {rendered}")

    # Example 5: Separate classes with different resource metadata
    print("\n2. CustomerDashboard (resource=CustomerContext):")
    customer_dash = lookup("CustomerDashboard", context)
    if customer_dash:
        rendered = customer_dash()
        print(f"   {rendered}")

    print("\n3. AdminDashboard (resource=AdminContext):")
    admin_dash = lookup("AdminDashboard", context)
    if admin_dash:
        rendered = admin_dash()
        print(f"   {rendered}")

    # Conditional decoration example
    print("\n4. AnalyticsWidget (conditionally decorated):")
    analytics = lookup("AnalyticsWidget", context)
    if analytics:
        rendered = analytics()
        print(f"   {rendered}")

    print("\n5. ReportingWidget (conditionally decorated - disabled):")
    try:
        reporting = lookup("ReportingWidget", context)
        if reporting:
            print("   (Should not be found)")
    except Exception as e:
        print(f"   Not found (as expected): {type(e).__name__}")

    print("\n" + "=" * 60)
    print("\nWhen to use direct application:")
    print("  1. Conditional decoration based on configuration")
    print("  2. Decorating classes from third-party libraries")
    print("  3. Applying different resource/location metadata to classes")
    print("  4. Dynamic component registration in plugins")
    print("  5. Testing scenarios requiring explicit control")
    print("\nKey points:")
    print("  1. injectable() can be called as a regular function")
    print("  2. Create separate classes for variants (CustomerDashboard, AdminDashboard)")
    print("  3. Apply injectable() with different resource metadata")
    print("  4. Each class registered by its own __name__")
    print("  5. Feature flags control which components are decorated")
    print("\nImportant:")
    print("  - Component name is always derived from class.__name__")
    print("  - To create variants, define separate classes")
    print("  - Resource/location metadata affects resolution, not naming")


if __name__ == "__main__":
    demonstrate_direct_decorator_application()
