from svcs_di import HopscotchRegistry

from examples.basic_tdom_injectable.services.counter import Counter
from examples.basic_tdom_injectable.services.database import DatabaseService


def svcs_setup(registry: HopscotchRegistry) -> None:
    """Configure the service registry for this application."""
    registry.register_factory(Counter, Counter)
    registry.register_factory(DatabaseService, DatabaseService)
