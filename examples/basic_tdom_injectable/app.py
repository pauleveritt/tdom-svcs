"""Application setup: registry, scanning, and container creation.

This module demonstrates the recommended production setup for tdom-svcs:
- Class components with @injectable decorator
- Automatic component scanning
- HopscotchInjector for production use
- ComponentLookup for string name resolution
"""

import svcs
from svcs_di.injectors.locator import HopscotchInjector

from tdom_svcs import ComponentNameRegistry, scan_components
from tdom_svcs.services.component_lookup import ComponentLookup


def setup_application() -> tuple[svcs.Registry, svcs.Container]:
    """
    Set up the application with dependency injection.

    This is the recommended production setup pattern. It includes:
    1. Service registration
    2. Component scanning for @injectable decorated classes
    3. HopscotchInjector for production-ready resolution
    4. ComponentLookup for component resolution by string name

    Returns:
        Tuple of (registry, container) ready for processing requests.
    """
    # Create svcs registry and component name registry
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()

    # Register services (non-component dependencies)
    # These will be injected into components via Inject[]
    from basic_tdom_injectable.services.auth import AuthService
    from basic_tdom_injectable.services.database import DatabaseService

    registry.register_value(DatabaseService, DatabaseService())
    registry.register_value(AuthService, AuthService())

    # Scan packages for @injectable components
    # This automatically registers components in both:
    # - ComponentNameRegistry (string name -> type)
    # - svcs.Registry (type -> factory)
    scan_components(
        registry,
        component_registry,
        "components",  # Relative import - scans components/ package
        "services",  # Also scan services (in case any are components)
    )

    # Register the component name registry itself (for ComponentLookup)
    registry.register_value(ComponentNameRegistry, component_registry)

    # Register HopscotchInjector (production injector with resource/location support)
    # NOTE: Use HopscotchInjector for production, not KeywordInjector
    registry.register_factory(HopscotchInjector, HopscotchInjector)

    # Register ComponentLookup service (resolves components by string name)
    def component_lookup_factory(container: svcs.Container) -> ComponentLookup:
        return ComponentLookup(container=container)

    registry.register_factory(ComponentLookup, component_lookup_factory)

    # Create container
    container = svcs.Container(registry)

    return registry, container


if __name__ == "__main__":
    # This allows testing the setup independently
    registry, container = setup_application()
    print("✓ Application setup complete")
    print("✓ Services registered: DatabaseService, AuthService")
    print("✓ Components scanned and registered from components/ package")
    print("✓ HopscotchInjector registered (production injector)")
    print("✓ ComponentLookup service available")
    print("✓ Container ready for requests")
