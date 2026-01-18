"""Async middleware example.

Demonstrates:
- Async middleware implementation with async __call__
- Mixed sync and async middleware in same execution chain
- Automatic async detection via inspect.iscoroutinefunction()
"""

import asyncio
from dataclasses import dataclass, field
from typing import Any, cast

from tdom_svcs.services.middleware import Context, MiddlewareManager


@dataclass
class SyncLoggingMiddleware:
    """Synchronous logging middleware."""

    priority: int = -10
    logged: list = field(default_factory=list)

    def __call__(self, component, props, context):
        self.logged.append(f"sync:{component.__name__}")
        return props


@dataclass
class AsyncDatabaseMiddleware:
    """Async middleware that fetches data from database."""

    priority: int = -5
    queries: list = field(default_factory=list)

    async def __call__(self, component, props, context):
        await asyncio.sleep(0.01)  # Simulate async database query
        self.queries.append(component.__name__)
        props["_db_user"] = {"id": 123, "name": "John Doe"}
        return props


@dataclass
class AsyncValidationMiddleware:
    """Async middleware that validates props."""

    priority: int = 5

    async def __call__(self, component, props, context):
        await asyncio.sleep(0.01)  # Simulate async validation
        if "invalid" in props:
            return None
        return props


@dataclass
class SyncTransformMiddleware:
    """Sync middleware that transforms async-enriched props."""

    priority: int = 10

    def __call__(self, component, props, context):
        if "_db_user" in props:
            user = props["_db_user"]
            props["_display_name"] = user["name"]
        return props


class Dashboard:
    """Example component."""

    def __init__(self, title: str, **kwargs):
        self.title = title


async def main() -> dict[str, Any]:
    """Execute mixed sync and async middleware chain."""
    manager = MiddlewareManager()

    # Register mixed middleware
    sync_logging = SyncLoggingMiddleware()
    async_db = AsyncDatabaseMiddleware()
    manager.register_middleware(sync_logging)
    manager.register_middleware(async_db)
    manager.register_middleware(AsyncValidationMiddleware())
    manager.register_middleware(SyncTransformMiddleware())

    context: Context = cast(Context, {"config": {}})

    # Execute async middleware chain
    props = {"title": "Main Dashboard"}
    result = await manager.execute_async(Dashboard, props, context)

    # Verify execution
    assert result is not None
    assert "_db_user" in result
    assert "_display_name" in result
    assert result["_display_name"] == "John Doe"
    assert "sync:Dashboard" in sync_logging.logged
    assert "Dashboard" in async_db.queries

    # Test validation failure
    invalid_result = await manager.execute_async(
        Dashboard, {"title": "Error", "invalid": True}, context
    )
    assert invalid_result is None

    return result


if __name__ == "__main__":
    print(asyncio.run(main()))
