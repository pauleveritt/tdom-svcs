"""Middleware for the scoping example.

Demonstrates:
- Global middleware (applies to all components)
- Per-component middleware (via @component decorator)
- Async middleware support
- Mixed sync and async chains

Global sync middleware use @middleware for automatic discovery.
Async middleware are registered manually when needed.
"""

import asyncio
from dataclasses import dataclass, field

from svcs_di.injectors import injectable

from tdom_svcs import middleware
from tdom_svcs.types import Component, Context, Props, PropsResult

# =============================================================================
# Global Middleware (discovered by scan)
# =============================================================================


# The global logging middleware runs for the whole app lifespan
@middleware
@dataclass
class GlobalLoggingMiddleware:
    """Global logging middleware that runs for all components.

    This middleware is discovered by scan() and applies to every
    component that goes through the middleware chain.
    """

    priority: int = -10
    logged: list[str] = field(default_factory=list)

    def __call__(
        self, component: Component, props: Props, context: Context
    ) -> PropsResult:
        component_name = getattr(component, "__name__", type(component).__name__)
        self.logged.append(f"global:{component_name}")
        return props


@middleware
@dataclass
class GlobalValidationMiddleware:
    """Global validation middleware that runs for all components."""

    priority: int = 0

    def __call__(
        self, component: Component, props: Props, context: Context
    ) -> PropsResult:
        if not props:
            return None
        return props


# =============================================================================
# Async Middleware (registered manually for async chains)
# =============================================================================


@injectable
@dataclass
class SyncTransformMiddleware:
    """Synchronous transformation middleware for async chains."""

    priority: int = 10

    def __call__(
        self, component: Component, props: Props, context: Context
    ) -> PropsResult:
        props["_sync_processed"] = True
        return props


@injectable
@dataclass
class AsyncDatabaseMiddleware:
    """Async middleware that simulates fetching data from a database.

    Demonstrates async middleware with async __call__ method.
    """

    priority: int = -5
    queries: list[str] = field(default_factory=list)

    async def __call__(
        self, component: Component, props: Props, context: Context
    ) -> PropsResult:
        component_name = getattr(component, "__name__", type(component).__name__)
        # Simulate async database query
        await asyncio.sleep(0.01)
        self.queries.append(component_name)
        props["_db_user"] = {"id": 123, "name": "John Doe"}
        return props


@injectable
@dataclass
class AsyncValidationMiddleware:
    """Async middleware that performs async validation."""

    priority: int = 5

    async def __call__(
        self, component: Component, props: Props, context: Context
    ) -> PropsResult:
        # Simulate async validation (e.g., checking external service)
        await asyncio.sleep(0.01)
        if props.get("invalid"):
            return None
        return props
