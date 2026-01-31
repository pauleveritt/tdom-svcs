"""Basic middleware example.

Demonstrates the recommended pattern for using middleware:
- Chain execution with multiple middleware
- Priority ordering (lower numbers run first)
- Halting execution by returning None
- Prop transformation
"""

from typing import cast

from svcs_di.injectors import HopscotchContainer, HopscotchRegistry
from svcs_di.injectors.scanning import scan

from examples.common import Greeting, Request
from examples.middleware.basic import components, services
from examples.middleware.basic.middleware import (
    LoggingMiddleware,
    TransformationMiddleware,
    ValidationMiddleware,
)
from tdom_svcs import html
from tdom_svcs.services.middleware import Context, MiddlewareManager, setup_container


def main() -> str:
    """Execute middleware chain and demonstrate all patterns."""
    registry = HopscotchRegistry()
    scan(registry, services, components)

    # Setup middleware manager
    context: Context = cast(Context, {"config": {"debug": True}})
    setup_container(context, registry)

    with HopscotchContainer(registry) as container:
        container.register_local_value(Request, Request(user_id="1"))

        # Get the middleware manager
        manager = container.get(MiddlewareManager)

        # Register middleware instances directly
        logging_mw = LoggingMiddleware()
        manager.register_middleware(logging_mw)
        manager.register_middleware(ValidationMiddleware())
        manager.register_middleware(TransformationMiddleware())

        # Test 1: Valid props (should pass all middleware)
        props = {"title": "Click Me", "variant": "primary"}
        result = manager.execute(Greeting, props, context)

        assert result is not None
        assert result["title"] == "Click Me"
        assert result["transformed"] is True
        assert "Greeting" in logging_mw.logged

        # Test 2: Invalid props (should halt at validation)
        invalid_props = {"variant": "secondary"}  # Missing 'title'
        halted_result = manager.execute(Greeting, invalid_props, context)

        assert halted_result is None

        # Test 3: Render Greeting component
        response = html(t"<{Greeting} />", context=container)
        result_html = str(response)

        assert "Hello Alice!" in result_html

        return result_html


if __name__ == "__main__":
    print(main())
