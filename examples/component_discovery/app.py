"""Component discovery example application.

This example demonstrates resolving multiple components with different
dependency patterns using direct type-based resolution.
"""

from svcs import Registry, Container
from svcs_di.injectors.locator import HopscotchInjector
from examples.component_discovery import site
from examples.component_discovery.components import Button, UserProfile, AdminPanel


def main() -> str:
    """Main application entry point."""
    registry = Registry()

    # Setup services from site.py
    site.svcs_setup(registry)

    # Register components - @injectable decorator marks them for DI
    registry.register_factory(Button, Button)
    registry.register_factory(UserProfile, UserProfile)
    registry.register_factory(AdminPanel, AdminPanel)

    # Register HopscotchInjector for dependency injection
    registry.register_factory(HopscotchInjector, HopscotchInjector)

    with Container(registry) as container:
        # Get the injector which handles Inject[] dependencies
        injector = container.get(HopscotchInjector)

        # Resolve components - injector handles Inject[] automatically
        button = injector(Button)
        profile = injector(UserProfile)
        panel = injector(AdminPanel)

        # Render components
        results = [
            button(),
            profile(),
            panel(),
        ]

        return "\n".join(results)


if __name__ == "__main__":
    print(main())
