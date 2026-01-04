from svcs import Registry, Container
from examples.basic_tdom_svcs import site
from examples.basic_tdom_svcs.components.greeting import greeting
from examples.basic_tdom_svcs.services.database import DatabaseService


def main() -> str:
    registry = Registry()

    # Custom setup from site.py
    site.svcs_setup(registry)

    with Container(registry) as container:
        result = greeting(db=container.get(DatabaseService))
        return result


if __name__ == "__main__":
    print(main())
