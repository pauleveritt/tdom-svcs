"""Middleware scoping example.

Demonstrates:
- Global middleware (applies to all components)
- Per-component middleware (via @component decorator)
- Async middleware support
- Mixed sync and async chains
"""

import asyncio
from typing import Any, cast

from svcs_di.injectors import HopscotchContainer, HopscotchRegistry
from svcs_di.injectors.scanning import scan

from examples.common import Greeting, Request
from examples.middleware.scoping import components, services
from examples.middleware.scoping.components import Button, Card, button_mw
from examples.middleware.scoping.middleware import (
    AsyncDatabaseMiddleware,
    AsyncValidationMiddleware,
    GlobalLoggingMiddleware,
    GlobalValidationMiddleware,
    SyncTransformMiddleware,
)
from tdom_svcs import html
from tdom_svcs.services.middleware import (
    Context,
    MiddlewareManager,
    get_component_middleware,
    setup_container,
)


async def main() -> str:
    """Execute global and per-component middleware with async support."""
    registry = HopscotchRegistry()
    scan(registry, services, components)

    # Setup middleware manager
    context: Context = cast(Context, {"config": {"debug": True}})
    setup_container(context, registry)

    with HopscotchContainer(registry) as container:
        container.register_local_value(Request, Request(user_id="1"))

        manager = container.get(MiddlewareManager)

        # Register global middleware
        global_logging = GlobalLoggingMiddleware()
        manager.register_middleware(global_logging)
        manager.register_middleware(GlobalValidationMiddleware())

        # Test 1: Button with per-component middleware
        button_props = {"title": "Click Me"}
        result = manager.execute(Button, button_props, context)
        assert result is not None

        # Execute per-component middleware
        component_mw = get_component_middleware(Button)
        for mw in component_mw.get("pre_resolution", []):
            mw_result = mw(Button, result, context)
            if isinstance(mw_result, dict):
                result = mw_result

        assert "global:Button" in global_logging.logged
        assert "button:Button" in button_mw.logged
        assert result["variant"] == "primary"

        # Test 2: Card without per-component middleware
        card_props = {"title": "Welcome", "content": "Hello there!"}
        card_result = manager.execute(Card, card_props, context)
        assert card_result is not None
        assert "global:Card" in global_logging.logged

        # Card has no per-component middleware
        card_mw = get_component_middleware(Card)
        assert not card_mw.get("pre_resolution", [])

        # Test 3: Async middleware chain
        # Create a new manager for async test
        async_manager = MiddlewareManager()
        sync_logging = GlobalLoggingMiddleware()
        async_db = AsyncDatabaseMiddleware()
        async_validation = AsyncValidationMiddleware()
        sync_transform = SyncTransformMiddleware()

        async_manager.register_middleware(sync_logging)
        async_manager.register_middleware(async_db)
        async_manager.register_middleware(async_validation)
        async_manager.register_middleware(sync_transform)

        # Execute async middleware chain using Greeting
        async_props = {"title": "Main Dashboard"}
        async_result = await async_manager.execute_async(Greeting, async_props, context)

        assert async_result is not None
        assert "_db_user" in async_result
        assert async_result["_db_user"]["name"] == "John Doe"
        assert "_sync_processed" in async_result

        # Test 4: Async validation failure
        invalid_result = await async_manager.execute_async(
            Greeting, {"title": "Error", "invalid": True}, context
        )
        assert invalid_result is None

        # Render Greeting component
        response = html(t"<{Greeting} />", context=container)
        result_html = str(response)

        assert "Hello Alice!" in result_html

        return result_html


if __name__ == "__main__":
    print(asyncio.run(main()))
