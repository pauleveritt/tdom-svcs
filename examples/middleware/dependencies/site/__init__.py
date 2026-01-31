"""A site that configures an app with testing fakes.

Demonstrates how to override services for testing purposes.
"""

from svcs_di.hopscotch_registry import HopscotchRegistry

from examples.middleware.dependencies.services import Logger
from examples.middleware.dependencies.site.services import FakeLogger


def svcs_registry(registry: HopscotchRegistry) -> None:
    """Called automatically during scan() - registers FakeLogger for testing."""
    registry.register_value(Logger, FakeLogger(name="TEST"))
