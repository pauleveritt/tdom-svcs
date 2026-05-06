"""Component override with imperative registration.

This example demonstrates:

- Overriding default components with site-specific implementations
- Using register_implementation() for explicit overrides
- App/site separation pattern
- Component replacement without changing app code
"""

from svcs_hopscotch.injectors import HopscotchContainer, HopscotchRegistry

from examples.hopscotch.override import app_common, site
from examples.hopscotch.override.app_common import Greeting, Request
from tdom_svcs import html, scan


def main() -> str:
    # docs: start app-scan
    registry = HopscotchRegistry()
    scan(registry, app_common, site)
    # docs: end app-scan

    # docs: start render-override
    with HopscotchContainer(registry) as container:
        container.register_local_value(Request, Request(user_id="1"))

        # Dataclass component: pass context container into the rendering
        response = html(t"<{Greeting} />", container=container)
        result = str(response)

        # We no longer use the default Greeting with "Hello"
        assert "Hello" not in result
        assert "Bonjour" in result

        return result
    # docs: end render-override


if __name__ == "__main__":
    print(main())
