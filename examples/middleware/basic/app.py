"""Basic middleware example.

Demonstrates the recommended pattern for using middleware:
- Chain execution with multiple middleware
- Priority ordering (lower numbers run first)
- Halting execution by returning None
- Prop transformation

This example uses Hopscotch patterns (decorators, scanning) for convenience.
You can also use imperative registration with register_middleware() if preferred.
"""

from svcs_di.injectors import HopscotchContainer, HopscotchRegistry

from examples.common import SimpleComponent
from examples.middleware.basic import middleware
from examples.middleware.basic.middleware import LoggingMiddleware
from tdom_svcs import execute_middleware, html, scan


def main() -> str:
    """Execute middleware chain and demonstrate all patterns."""
    # Create registry and scan for @injectable and @middleware
    registry = HopscotchRegistry()
    scan(registry, middleware)

    with HopscotchContainer(registry) as container:
        # Get logging middleware for verification
        logging_mw = container.get(LoggingMiddleware)

        # Test 1: Valid props (should pass all middleware)
        props = {"title": "Click Me", "variant": "primary"}
        result = execute_middleware(SimpleComponent, props, container)

        assert result is not None
        assert result["title"] == "Click Me"
        assert result["transformed"] is True
        assert "SimpleComponent" in logging_mw.logged

        # Test 2: Invalid props (should halt at validation)
        invalid_props = {"variant": "secondary"}  # Missing 'title'
        halted_result = execute_middleware(SimpleComponent, invalid_props, container)

        assert halted_result is None

        # Render component
        response = html(t"<{SimpleComponent} />", context=container)
        return str(response)


if __name__ == "__main__":
    print(main())
