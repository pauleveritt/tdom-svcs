"""Basic tdom-svcs with @injectable decorator example.

Demonstrates using HopscotchContainer with tdom templates and
@injectable decorated components.
"""

from svcs_di import HopscotchContainer, HopscotchRegistry

from examples.basic_tdom_injectable import site
from examples.basic_tdom_injectable.components.dashboard import Dashboard


def main() -> str:
    """Render a dashboard with injected counter service."""
    registry = HopscotchRegistry()

    # Custom setup from site.py
    site.svcs_setup(registry)

    # Register @injectable components
    registry.register_factory(Dashboard, Dashboard)

    with HopscotchContainer(registry) as container:
        dashboard = container.inject(Dashboard)  # ty: ignore[unresolved-attribute]
        result = str(dashboard())

        assert "dashboard" in result
        assert "Counter:" in result

        return result


if __name__ == "__main__":
    print(main())
