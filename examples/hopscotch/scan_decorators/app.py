"""Component override with @injectable decorator.

This example demonstrates:

- Automatic override discovery using @injectable(for_=...)
- Declarative component replacement with decorators
- Scan discovering both original and override implementations
- Site-level overrides registered automatically
"""

from svcs_hopscotch.injectors import HopscotchContainer, HopscotchRegistry

from examples.hopscotch.scan_decorators import components, services, site
from examples.hopscotch.scan_decorators.components import Greeting
from examples.hopscotch.scan_decorators.request import Request
from tdom_svcs import html, scan


def main() -> str:
    registry = HopscotchRegistry()
    scan(registry, components, services, site)

    with HopscotchContainer(registry) as container:
        container.register_local_value(Request, Request(user_id="1"))

        # Dataclass component: pass context container into the rendering
        response = html(t"<{Greeting} />", container=container)
        result = str(response)

        # We no longer use the default Greeting with "Hello"
        assert "Hello" not in result
        assert "Bonjour" in result

        return result


if __name__ == "__main__":
    print(main())
