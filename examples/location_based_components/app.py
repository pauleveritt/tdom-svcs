"""Location-based component resolution example.

Demonstrates how different components are resolved based on PurePath location
in the container context using HopscotchContainer.
"""

from pathlib import PurePath

from svcs_di import HopscotchContainer, HopscotchRegistry

from examples.location_based_components import site
from examples.location_based_components.components import AdminPanel, HomePage


def main() -> str:
    """Resolve components based on URL path location."""
    registry = HopscotchRegistry()

    # Setup services from site.py
    site.svcs_setup(registry)

    # Register components with location metadata
    registry.register_factory(HomePage, HomePage)
    registry.register_factory(AdminPanel, AdminPanel)

    with HopscotchContainer(registry) as container:
        # Register location context for home page
        container.register_local_value(PurePath, PurePath("/"))

        # Resolve HomePage (matches "/" location)
        page = container.inject(HomePage)
        result = str(page())

        assert "Home:" in result

        return result


if __name__ == "__main__":
    print(main())
