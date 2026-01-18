"""Middleware system example.

Demonstrates using MiddlewareManager with global and per-component middleware
for component lifecycle hooks.
"""

from typing import cast

from svcs_di import HopscotchContainer, HopscotchRegistry

from examples.middleware import site
from examples.middleware.components import Button
from examples.middleware.site import GlobalLoggingMiddleware
from tdom_svcs.services.middleware import (
    Context,
    MiddlewareManager,
    get_component_middleware,
)


def main() -> dict:
    """Execute middleware chain on a component."""
    registry = HopscotchRegistry()
    context: Context = cast(Context, {"config": {"debug": True}})

    # Custom setup from site.py
    site.svcs_setup(registry, context)

    with HopscotchContainer(registry) as container:
        manager = container.get(MiddlewareManager)
        manager.register_middleware(GlobalLoggingMiddleware())

        props = {"title": "Submit"}

        # Execute global middleware
        result = manager.execute(Button, props, context)
        assert result is not None

        # Execute per-component middleware
        component_middleware = get_component_middleware(Button)
        for mw in component_middleware.get("pre_resolution", []):
            result = mw(Button, result, context)
            if result is None:
                break

        assert result is not None
        assert "title" in result

        return result


if __name__ == "__main__":
    print(main())
