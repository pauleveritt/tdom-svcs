"""Middleware scoping example.

Demonstrates:
- Global middleware (applies to all components)
- Per-component middleware (via @component decorator)
- Async middleware support
- Mixed sync and async chains

This example uses Hopscotch patterns (decorators, scanning) for convenience.
You can also use imperative registration with register_middleware() if preferred.
"""

import asyncio

from svcs_di.injectors import HopscotchContainer, HopscotchRegistry

from examples.common import SimpleComponent
from examples.middleware.scoping import components, middleware
from examples.middleware.scoping.components import (
    Button,
    ButtonSpecificMiddleware,
    Card,
)
from examples.middleware.scoping.middleware import (
    AsyncDatabaseMiddleware,
    AsyncValidationMiddleware,
    GlobalLoggingMiddleware,
    SyncTransformMiddleware,
)
from tdom_svcs import (
    execute_component_middleware,
    execute_middleware,
    execute_middleware_async,
    get_component_middleware,
    html,
    register_middleware,
    scan,
)


async def main() -> str:
    """Execute global and per-component middleware with async support."""
    # Create registry and scan for @injectable, @middleware, and @component
    registry = HopscotchRegistry()
    scan(registry, middleware, components)

    with HopscotchContainer(registry) as container:
        # Get global logging middleware for verification
        global_logging = container.get(GlobalLoggingMiddleware)
        # Get button-specific middleware for verification
        button_mw = container.get(ButtonSpecificMiddleware)

        # Test 1: Button with per-component middleware
        button_props = {"title": "Click Me"}
        result = execute_middleware(Button, button_props, container)
        assert result is not None

        # Execute per-component middleware (resolves types from container)
        result = execute_component_middleware(
            Button, result, container, "pre_resolution"
        )
        assert result is not None

        assert "global:Button" in global_logging.logged
        assert "button:Button" in button_mw.logged
        assert result["variant"] == "primary"

        # Test 2: Card without per-component middleware
        card_props = {"title": "Welcome", "content": "Hello there!"}
        card_result = execute_middleware(Card, card_props, container)
        assert card_result is not None
        assert "global:Card" in global_logging.logged

        # Card has no per-component middleware
        card_mw = get_component_middleware(registry, Card)
        assert not card_mw.get("pre_resolution", [])

        # Test 3: Async middleware chain
        # Register async middleware imperatively for the async test
        register_middleware(registry, AsyncDatabaseMiddleware)
        register_middleware(registry, AsyncValidationMiddleware)
        register_middleware(registry, SyncTransformMiddleware)

        # Execute async middleware chain
        async_props = {"title": "Main Dashboard"}
        async_result = await execute_middleware_async(
            SimpleComponent, async_props, container
        )

        assert async_result is not None
        assert "_db_user" in async_result
        assert async_result["_db_user"]["name"] == "John Doe"
        assert "_sync_processed" in async_result

        # Test 4: Async validation failure
        invalid_result = await execute_middleware_async(
            SimpleComponent, {"title": "Error", "invalid": True}, container
        )
        assert invalid_result is None

        # Render component
        response = html(t"<{SimpleComponent} />", context=container)
        return str(response)


if __name__ == "__main__":
    print(asyncio.run(main()))
