"""Resource-based component resolution example.

Demonstrates how different components are resolved based on resource type
(e.g., CustomerContext vs AdminContext) using HopscotchContainer.
"""

from svcs_di import HopscotchContainer, HopscotchRegistry

from examples.resource_based_components import site
from examples.resource_based_components.components import AdminDashboard, CustomerDashboard
from examples.resource_based_components.services.contexts import CustomerContext


def main() -> str:
    """Resolve components based on resource context type."""
    registry = HopscotchRegistry()

    # Setup services from site.py
    site.svcs_setup(registry)

    # Register components with resource metadata
    registry.register_factory(CustomerDashboard, CustomerDashboard)
    registry.register_factory(AdminDashboard, AdminDashboard)

    with HopscotchContainer(registry) as container:
        # Register resource context for customer
        container.register_local_value(type, CustomerContext())

        # Resolve CustomerDashboard (matches CustomerContext resource)
        dashboard = container.inject(CustomerDashboard, resource=CustomerContext)
        result = str(dashboard())

        assert "Customer Dashboard" in result
        assert "visits" in result

        return result


if __name__ == "__main__":
    print(main())
