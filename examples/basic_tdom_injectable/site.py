from svcs import Registry
from examples.basic_tdom_injectable.services.counter import Counter
from examples.basic_tdom_injectable.services.database import DatabaseService


def svcs_setup(registry: Registry):
    """Configure the service registry for this application."""
    registry.register_factory(DatabaseService, DatabaseService)
