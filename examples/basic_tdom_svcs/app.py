"""Basic tdom-svcs with function component example.

Demonstrates a simple function component that receives a service
directly from the container.
"""

from svcs_di import HopscotchContainer, HopscotchRegistry

from examples.basic_tdom_svcs import site
from examples.basic_tdom_svcs.components.greeting import greeting
from examples.basic_tdom_svcs.services.database import DatabaseService


def main() -> str:
    """Render a greeting with database user count."""
    registry = HopscotchRegistry()

    # Custom setup from site.py
    site.svcs_setup(registry)

    with HopscotchContainer(registry) as container:
        node = greeting(db=container.get(DatabaseService))
        result = str(node)

        assert "Hello from tdom_svcs" in result
        assert "Users:" in result

        return result


if __name__ == "__main__":
    print(main())
