"""Resource-based components example application.

This example demonstrates how to use resource-based component resolution
with HopscotchInjector. Different components are resolved based on the
resource type in the container context.
"""

from svcs import Registry, Container
from svcs_di.injectors.locator import HopscotchInjector
from examples.resource_based_components import site
from examples.resource_based_components.components import CustomerDashboard, AdminDashboard
from examples.resource_based_components.services.contexts import CustomerContext


def main() -> str:
    """Main application entry point."""
    registry = Registry()

    # Setup services from site.py
    site.svcs_setup(registry)

    # Register components - HopscotchInjector uses their @injectable metadata
    registry.register_factory(CustomerDashboard, CustomerDashboard)
    registry.register_factory(AdminDashboard, AdminDashboard)

    # Register injector
    registry.register_factory(HopscotchInjector, HopscotchInjector)

    with Container(registry) as container:
        # Push a resource context to select which dashboard variant to use
        container.register_local_value(type, CustomerContext())

        # Get the injector and construct the CustomerDashboard
        # (because CustomerContext resource is in the container)
        injector = container.get(HopscotchInjector)
        dashboard = injector(CustomerDashboard)

        return dashboard()


if __name__ == "__main__":
    print(main())
