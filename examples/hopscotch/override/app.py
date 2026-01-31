"""Customize the app by replacing the component."""

from svcs_di.injectors import HopscotchContainer, HopscotchRegistry
from svcs_di.injectors.scanning import scan

from examples.hopscotch.override import app_common, site
from examples.hopscotch.override.app_common import Greeting, Request
from tdom_svcs import html


def main() -> str:
    registry = HopscotchRegistry()
    scan(registry, app_common, site)

    with HopscotchContainer(registry) as container:
        container.register_local_value(Request, Request(user_id="1"))

        # Dataclass component: pass context container into the rendering
        response = html(t"<{Greeting} />", context=container)
        result = str(response)

        # We no longer use the default Greeting with "Hello"
        assert "Hello" not in result
        assert "Bonjour" in result

        return result


if __name__ == "__main__":
    print(main())
