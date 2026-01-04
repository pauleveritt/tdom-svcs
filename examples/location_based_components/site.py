"""Application setup for location-based components example."""

import svcs
from examples.location_based_components.services.auth import AuthService
from examples.location_based_components.services.content import ContentService


def svcs_setup(registry: svcs.Registry) -> None:
    """Register services in the svcs registry."""
    registry.register_factory(AuthService, AuthService)
    registry.register_factory(ContentService, ContentService)
