"""Application setup for resource-based components example."""

import svcs
from examples.resource_based_components.services.user import UserService
from examples.resource_based_components.services.analytics import AnalyticsService


def svcs_setup(registry: svcs.Registry) -> None:
    """Register services in the svcs registry."""
    # Register services
    registry.register_factory(UserService, UserService)
    registry.register_factory(AnalyticsService, AnalyticsService)
