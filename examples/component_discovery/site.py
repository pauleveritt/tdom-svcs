"""Application setup for component discovery example."""

import svcs
from examples.component_discovery.services.database import DatabaseService
from examples.component_discovery.services.auth import AuthService


def svcs_setup(registry: svcs.Registry) -> None:
    """Register services in the svcs registry."""
    registry.register_factory(DatabaseService, DatabaseService)
    registry.register_factory(AuthService, AuthService)
