"""Application setup for direct decorator example."""

import svcs
from svcs_di.injectors.locator import HopscotchInjector

from tdom_svcs import ComponentNameRegistry, scan_components
from tdom_svcs.services.component_lookup import ComponentLookup

from direct_decorator.services import ThemeService


def setup_application():
    """Setup application with programmatically decorated components."""
    # Create registries
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()

    # Register services
    theme_service = ThemeService()
    registry.register_value(ThemeService, theme_service)

    # Scan for @injectable components
    # This will find Card, CustomerDashboard, AdminDashboard, and AnalyticsWidget
    scan_components(registry, component_registry, "direct_decorator")

    # Setup container
    container = svcs.Container(registry)
    registry.register_value(ComponentNameRegistry, component_registry)
    registry.register_factory(HopscotchInjector, HopscotchInjector)

    # Create ComponentLookup
    lookup = ComponentLookup(container=container)

    return lookup, component_registry
