"""Middleware for the scoping example.

Demonstrates:
- Global middleware (applies to all components)
- Per-component middleware (via @component decorator)
- Async middleware support
- Mixed sync and async chains
"""

import asyncio
from dataclasses import dataclass, field
from typing import Any


@dataclass
class GlobalLoggingMiddleware:
    """Global logging middleware that runs for all components.

    This middleware is registered with MiddlewareManager and applies
    to every component that goes through the middleware chain.
    """

    priority: int = -10
    logged: list[str] = field(default_factory=list)

    def __call__(
        self, component: type, props: dict[str, Any], context: Any
    ) -> dict[str, Any]:
        component_name = (
            component.__name__ if hasattr(component, "__name__") else str(component)
        )
        self.logged.append(f"global:{component_name}")
        return props


@dataclass
class GlobalValidationMiddleware:
    """Global validation middleware that runs for all components."""

    priority: int = 0

    def __call__(
        self, component: type, props: dict[str, Any], context: Any
    ) -> dict[str, Any] | None:
        if not props:
            return None
        return props


@dataclass
class SyncTransformMiddleware:
    """Synchronous transformation middleware."""

    priority: int = 10

    def __call__(
        self, component: type, props: dict[str, Any], context: Any
    ) -> dict[str, Any]:
        props["_sync_processed"] = True
        return props


@dataclass
class AsyncDatabaseMiddleware:
    """Async middleware that simulates fetching data from a database.

    Demonstrates async middleware with async __call__ method.
    """

    priority: int = -5
    queries: list[str] = field(default_factory=list)

    async def __call__(
        self, component: type, props: dict[str, Any], context: Any
    ) -> dict[str, Any]:
        component_name = (
            component.__name__ if hasattr(component, "__name__") else str(component)
        )
        # Simulate async database query
        await asyncio.sleep(0.01)
        self.queries.append(component_name)
        props["_db_user"] = {"id": 123, "name": "John Doe"}
        return props


@dataclass
class AsyncValidationMiddleware:
    """Async middleware that performs async validation."""

    priority: int = 5

    async def __call__(
        self, component: type, props: dict[str, Any], context: Any
    ) -> dict[str, Any] | None:
        # Simulate async validation (e.g., checking external service)
        await asyncio.sleep(0.01)
        if props.get("invalid"):
            return None
        return props
