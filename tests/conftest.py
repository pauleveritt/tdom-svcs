"""Shared test fixtures for tdom-svcs tests."""

from dataclasses import dataclass

import pytest
from svcs_di.injectors import HopscotchContainer, HopscotchRegistry

from tdom_svcs.types import Component, Context, Middleware, Props, PropsResult


# =============================================================================
# Mock Services
# =============================================================================


class DatabaseService:
    """Mock database service for testing DI."""

    def get_user(self) -> str:
        return "Alice"


class AuthService:
    """Mock auth service for testing DI."""

    def is_authenticated(self) -> bool:
        return True


# =============================================================================
# Registry and Container Fixtures
# =============================================================================


@pytest.fixture
def registry() -> HopscotchRegistry:
    """Create a fresh HopscotchRegistry for testing."""
    return HopscotchRegistry()


@pytest.fixture
def container(registry: HopscotchRegistry):
    """Create a HopscotchContainer from registry."""
    with HopscotchContainer(registry) as container:
        yield container


# =============================================================================
# Middleware Test Fixtures
# =============================================================================


def create_tracking_middleware(
    name: str, default_priority: int = 0, *, halt: bool = False, is_async: bool = False
) -> type:
    """Factory for creating middleware classes that track execution order.

    Args:
        name: Name to record in execution order tracking
        default_priority: Middleware priority (lower = earlier)
        halt: If True, middleware returns None to halt execution
        is_async: If True, creates an async middleware (structural typing only)

    Returns:
        A middleware class (sync inherits from Middleware, async uses structural typing)
    """
    _halt = halt
    _name = name
    _default_priority = default_priority

    if is_async:
        # Note: Async middleware uses structural typing rather than inheriting
        # from Middleware, since async def __call__ has a different signature.
        @dataclass
        class AsyncTrackingMiddleware:
            priority: int = _default_priority

            async def __call__(
                self,
                component: Component,
                props: Props,
                context: Context,
            ) -> PropsResult:
                if _halt:
                    return None
                props[_name] = True
                if "_execution_order" not in props:
                    props["_execution_order"] = []
                props["_execution_order"].append(_name)
                return props

        AsyncTrackingMiddleware.__name__ = f"{_name.title()}Middleware"
        return AsyncTrackingMiddleware
    else:

        @dataclass
        class TrackingMiddleware(Middleware):
            priority: int = _default_priority

            def __call__(
                self,
                component: Component,
                props: Props,
                context: Context,
            ) -> PropsResult:
                if _halt:
                    return None
                props[_name] = True
                if "_execution_order" not in props:
                    props["_execution_order"] = []
                props["_execution_order"].append(_name)
                return props

        TrackingMiddleware.__name__ = f"{_name.title()}Middleware"
        return TrackingMiddleware


# Pre-built middleware classes for common test patterns
LowPriorityMiddleware = create_tracking_middleware("low", default_priority=-10)
DefaultPriorityMiddleware = create_tracking_middleware("default", default_priority=0)
HighPriorityMiddleware = create_tracking_middleware("high", default_priority=10)
HaltingMiddleware = create_tracking_middleware("halt", default_priority=0, halt=True)
AsyncMiddleware = create_tracking_middleware("async", default_priority=5, is_async=True)
