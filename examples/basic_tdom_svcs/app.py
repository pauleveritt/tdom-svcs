"""Application setup: registry and injector configuration.

This module demonstrates the simplest tdom-svcs setup using KeywordInjector
for function components. This pattern is for educational purposes only.

For production use, see basic_tdom_injectable example.
"""

import svcs
from svcs_di.injectors.keyword import KeywordInjector

from basic_tdom_svcs.services.database import DatabaseService


def setup_application() -> tuple[svcs.Registry, svcs.Container]:
    """
    Set up the application with dependency injection for function components.

    This setup uses KeywordInjector, which is appropriate for simple function
    components that are called directly (not resolved by string name).

    Returns:
        Tuple of (registry, container) ready for use.
    """
    # Create svcs registry
    registry = svcs.Registry()

    # Register services (these will be injected into components)
    registry.register_value(DatabaseService, DatabaseService())

    # Register KeywordInjector for function component injection
    # NOTE: KeywordInjector is for educational/simple examples only
    # Production code should use HopscotchInjector with class components
    registry.register_factory(KeywordInjector, KeywordInjector)

    # Create container
    container = svcs.Container(registry)

    return registry, container


if __name__ == "__main__":
    # This allows testing the setup independently
    registry, container = setup_application()
    print("✓ Application setup complete")
    print("✓ Registry configured with DatabaseService")
    print("✓ KeywordInjector registered for function components")
    print("✓ Container ready for use")
    print()
    print("NOTE: This example uses KeywordInjector for educational purposes.")
    print("      Production code should use HopscotchInjector with class components.")
