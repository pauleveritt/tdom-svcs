"""Inject a service into a service with svcs_di.auto"""

from svcs_di.injectors import HopscotchContainer, HopscotchRegistry
from svcs_di.injectors.scanning import scan

from examples.hopscotch.app_site import app_common, site
from examples.hopscotch.app_site.app_common import Greeting, Request
from tdom_svcs import html


def main() -> str:
    registry = HopscotchRegistry()
    scan(registry, app_common, site)

    with HopscotchContainer(registry) as container:
        request = Request(user_id="1")
        container.register_local_value(Request, request)

        # Dataclass component: pass context container into the rendering
        response = html(t"<{Greeting} />", context=container)
        result = str(response)
        assert "Alice" in result

        return result


if __name__ == "__main__":
    print(main())
