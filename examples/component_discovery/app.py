"""Application setup: registry, scanning, and container creation."""

import svcs
from svcs_di.injectors.locator import HopscotchInjector

from tdom_svcs import ComponentNameRegistry, scan_components
from tdom_svcs.services.component_lookup import ComponentLookup


def setup_application() -> tuple[svcs.Registry, svcs.Container]:
    """
    Set up the application with dependency injection.

    Returns:
        Tuple of (registry, container) ready for use.
    """
    # Create registries
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()

    # Register services
    from component_discovery.services.auth import AuthService
    from component_discovery.services.database import DatabaseService

    registry.register_value(DatabaseService, DatabaseService())
    registry.register_value(AuthService, AuthService())

    # Scan for @injectable components
    scan_components(
        registry,
        component_registry,
        "components",
        "services",
    )

    # Register component registry and injector
    registry.register_value(ComponentNameRegistry, component_registry)
    registry.register_factory(HopscotchInjector, HopscotchInjector)

    # Register ComponentLookup
    def component_lookup_factory(container: svcs.Container) -> ComponentLookup:
        return ComponentLookup(container=container)

    registry.register_factory(ComponentLookup, component_lookup_factory)

    # Create container
    container = svcs.Container(registry)

    return registry, container


if __name__ == "__main__":
    registry, container = setup_application()
    print("✓ Application setup complete")
    print("✓ Components scanned: Button, UserProfile, AdminPanel")
