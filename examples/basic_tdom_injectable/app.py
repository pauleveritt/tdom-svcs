from svcs import Registry, Container
from examples.basic_tdom_injectable import site
from examples.basic_tdom_injectable.components.dashboard import Dashboard


def main() -> str:
    registry = Registry()

    # Custom setup from site.py
    site.svcs_setup(registry)

    # Register @injectable components
    registry.register_factory(Dashboard, Dashboard)

    with Container(registry) as container:
        dashboard = container.get(Dashboard)
        return str(dashboard())


if __name__ == "__main__":
    print(main())
