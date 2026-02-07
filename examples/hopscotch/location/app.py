"""Location-based component resolution.

This example demonstrates:

- Varying component implementations based on URL path location
- Using HopscotchContainer with location= parameter
- Site-level component overrides for specific paths (e.g., /fr/)
- Multi-location testing in a single application
"""

from pathlib import PurePath

from svcs_di.injectors import HopscotchContainer, HopscotchRegistry

from examples.hopscotch.location import components, services, site
from examples.hopscotch.location.components import Greeting
from examples.hopscotch.location.request import Request
from tdom_svcs import html, scan


def main() -> list[str]:
    registry = HopscotchRegistry()
    scan(registry, components, services, site)

    results: list[str] = []

    # First request: default location (no special path)
    with HopscotchContainer(registry, location=PurePath("/en/users/1")) as container:
        container.register_local_value(Request, Request(user_id="1"))
        response = html(t"<{Greeting} />", context=container)
        result = str(response)

        # Default Greeting uses Hello
        assert "Hello Alice" in result
        results.append(result)

    # Second request: French location
    with HopscotchContainer(registry, location=PurePath("/fr/users/1")) as container:
        container.register_local_value(Request, Request(user_id="1"))
        response = html(t"<{Greeting} />", context=container)
        result = str(response)

        # FrenchGreeting uses Bonjour
        assert "Bonjour Alice" in result
        results.append(result)

    return results


if __name__ == "__main__":
    print(main())
