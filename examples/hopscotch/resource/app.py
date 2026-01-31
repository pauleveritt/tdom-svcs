"""Customize the app by replacing the component."""

from svcs_di.injectors import HopscotchContainer, HopscotchRegistry
from svcs_di.injectors.scanning import scan

from examples.hopscotch.resource import components, services, site
from examples.hopscotch.resource.components import Greeting
from examples.hopscotch.resource.request import Request
from examples.hopscotch.resource.resources import DefaultCustomer
from examples.hopscotch.resource.site.resources import FrenchCustomer
from tdom_svcs import html


def main() -> list[str]:
    registry = HopscotchRegistry()
    scan(registry, components, services, site)

    results: list[str] = []

    # First request: a regular customer
    default_customer = DefaultCustomer(name="Alice")
    with HopscotchContainer(registry, resource=default_customer) as container:
        container.register_local_value(Request, Request(user_id="1"))
        response = html(t"<{Greeting} />", context=container)
        result = str(response)

        # DefaultGreeting uses Hello
        assert "Hello Alice" in result
        results.append(result)

    # Second request: a French customer
    french_customer = FrenchCustomer(name="Marie")
    with HopscotchContainer(registry, resource=french_customer) as container:
        container.register_local_value(Request, Request(user_id="1"))
        response = html(t"<{Greeting} />", context=container)
        result = str(response)

        # FrenchGreeting uses Bonjour
        assert "Bonjour Marie" in result
        results.append(result)
    return results


if __name__ == "__main__":
    print(main())
