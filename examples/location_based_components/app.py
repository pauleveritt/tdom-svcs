"""Location-based components example application.

This example demonstrates how to use location-based component resolution
with HopscotchInjector. Different components are resolved based on the
PurePath location in the container context.
"""

from pathlib import PurePath
from svcs import Registry, Container
from svcs_di.injectors.locator import HopscotchInjector
from examples.location_based_components import site
from examples.location_based_components.components import HomePage, AdminPanel


def main() -> str:
    """Main application entry point."""
    registry = Registry()

    # Setup services from site.py
    site.svcs_setup(registry)

    # Register components - HopscotchInjector uses their @injectable metadata
    registry.register_factory(HomePage, HomePage)
    registry.register_factory(AdminPanel, AdminPanel)

    # Register injector
    registry.register_factory(HopscotchInjector, HopscotchInjector)

    with Container(registry) as container:
        # Push a location context to select which page component to use
        container.register_local_value(PurePath, PurePath("/"))

        # Get the injector and construct the HomePage
        # (because PurePath("/") is in the container)
        injector = container.get(HopscotchInjector)
        page = injector(HomePage)

        return page()


if __name__ == "__main__":
    print(main())
