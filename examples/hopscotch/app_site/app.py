"""Inject a service into a service with svcs_di.auto"""

from svcs_hopscotch.injectors import HopscotchContainer, HopscotchRegistry

from examples.hopscotch.app_site import app_common, site
from examples.hopscotch.app_site.app_common import Greeting, Request
from tdom_svcs import html, scan


def main() -> str:
    # docs: start app-scan
    registry = HopscotchRegistry()
    scan(registry, app_common, site)
    # docs: end app-scan

    # docs: start render-component
    with HopscotchContainer(registry) as container:
        request = Request(user_id="1")
        container.register_local_value(Request, request)

        # Dataclass component: pass context container into the rendering
        response = html(t"<{Greeting} />", container=container)
        result = str(response)
        assert "Alice" in result

        return result
    # docs: end render-component


if __name__ == "__main__":
    print(main())
