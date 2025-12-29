"""
Tests for MiddlewareManager.

This module tests the MiddlewareManager class which manages middleware
registration and execution with priority-based ordering and async support.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, cast

import pytest

from tdom_svcs.services.middleware import Context, MiddlewareManager

# Test fixtures - middleware implementations


@dataclass
class LowPriorityMiddleware:
    """Middleware that runs early (priority -10)."""

    priority: int = -10
    executed: list[str] = field(default_factory=list)  # Track execution order

    def __call__(
        self,
        component: type | Callable[..., Any],
        props: dict[str, Any],
        context: Context,
    ) -> dict[str, Any] | None:
        """Execute middleware and track order."""
        self.executed.append("low")
        props["low"] = True
        return props


@dataclass
class DefaultPriorityMiddleware:
    """Middleware that runs at default priority (0)."""

    priority: int = 0
    executed: list[str] = field(default_factory=list)

    def __call__(
        self,
        component: type | Callable[..., Any],
        props: dict[str, Any],
        context: Context,
    ) -> dict[str, Any] | None:
        """Execute middleware and track order."""
        self.executed.append("default")
        props["default"] = True
        return props


@dataclass
class HighPriorityMiddleware:
    """Middleware that runs late (priority 10)."""

    priority: int = 10
    executed: list[str] = field(default_factory=list)

    def __call__(
        self,
        component: type | Callable[..., Any],
        props: dict[str, Any],
        context: Context,
    ) -> dict[str, Any] | None:
        """Execute middleware and track order."""
        self.executed.append("high")
        props["high"] = True
        return props


@dataclass
class HaltingMiddleware:
    """Middleware that halts execution by returning None."""

    priority: int = 0

    def __call__(
        self,
        component: type | Callable[..., Any],
        props: dict[str, Any],
        context: Context,
    ) -> dict[str, Any] | None:
        """Return None to halt execution."""
        return None


@dataclass
class AsyncMiddleware:
    """Async middleware implementation."""

    priority: int = 5
    executed: list[str] = field(default_factory=list)

    async def __call__(
        self,
        component: type | Callable[..., Any],
        props: dict[str, Any],
        context: Context,
    ) -> dict[str, Any] | None:
        """Async middleware execution."""
        self.executed.append("async")
        props["async"] = True
        return props


class Button:
    """Test class component."""

    def __init__(self, label: str = "Click"):
        self.label = label


def heading(text: str = "Heading") -> str:
    """Test function component."""
    return f"<h1>{text}</h1>"


def test_middleware_manager_register_and_execute():
    """Test registering middleware and basic execution."""
    manager = MiddlewareManager()
    middleware = DefaultPriorityMiddleware()
    manager.register_middleware(middleware)

    props = {"label": "Click"}
    context: Context = cast(Context, {})

    result = manager.execute(Button, props, context)

    assert result is not None
    assert result["label"] == "Click"
    assert result["default"] is True


def test_middleware_manager_priority_ordering():
    """Test middleware executes in priority order (lower numbers first)."""
    manager = MiddlewareManager()

    # Track execution order with shared list
    execution_order: list[str] = []
    high = HighPriorityMiddleware(executed=execution_order)
    low = LowPriorityMiddleware(executed=execution_order)
    default = DefaultPriorityMiddleware(executed=execution_order)

    # Register in random order
    manager.register_middleware(high)
    manager.register_middleware(low)
    manager.register_middleware(default)

    props = {}
    context: Context = cast(Context, {})

    result = manager.execute(Button, props, context)

    # Should execute in priority order: low (-10), default (0), high (10)
    assert execution_order == ["low", "default", "high"]
    assert result is not None
    assert result["low"] is True
    assert result["default"] is True
    assert result["high"] is True


def test_middleware_manager_halt_on_none():
    """Test execution halts when middleware returns None."""
    manager = MiddlewareManager()

    # Track execution order
    execution_order: list[str] = []
    low = LowPriorityMiddleware(priority=-10, executed=execution_order)
    halting = HaltingMiddleware(priority=0)
    high = HighPriorityMiddleware(priority=10, executed=execution_order)

    manager.register_middleware(low)
    manager.register_middleware(halting)
    manager.register_middleware(high)

    props = {}
    context: Context = cast(Context, {})

    result = manager.execute(Button, props, context)

    # Execution should halt at halting middleware
    # Low priority runs, halting runs and returns None, high never runs
    assert execution_order == ["low"]
    assert result is None
    assert "low" in props
    assert "high" not in props


def test_middleware_manager_with_function_component():
    """Test middleware execution with function component."""
    manager = MiddlewareManager()
    middleware = DefaultPriorityMiddleware()
    manager.register_middleware(middleware)

    props = {"text": "Welcome"}
    context: Context = cast(Context, {})

    result = manager.execute(heading, props, context)

    assert result is not None
    assert result["text"] == "Welcome"
    assert result["default"] is True
    # Verify it's a function component
    assert not isinstance(heading, type)


def test_middleware_manager_with_class_component():
    """Test middleware execution with class component."""
    manager = MiddlewareManager()
    middleware = DefaultPriorityMiddleware()
    manager.register_middleware(middleware)

    props = {"label": "Submit"}
    context: Context = cast(Context, {})

    result = manager.execute(Button, props, context)

    assert result is not None
    assert result["label"] == "Submit"
    assert result["default"] is True
    # Verify it's a class component
    assert isinstance(Button, type)


@pytest.mark.anyio
async def test_middleware_manager_async_middleware():
    """Test execution with async middleware using anyio."""
    manager = MiddlewareManager()

    execution_order: list[str] = []
    sync_middleware = LowPriorityMiddleware(priority=-10, executed=execution_order)
    async_middleware = AsyncMiddleware(priority=5, executed=execution_order)
    sync_middleware2 = HighPriorityMiddleware(priority=10, executed=execution_order)

    manager.register_middleware(sync_middleware)
    # Type checker can't detect async __call__ satisfies protocol at static analysis time
    # Runtime detection via inspect.iscoroutinefunction() handles this correctly
    manager.register_middleware(async_middleware)  # type: ignore[arg-type]
    manager.register_middleware(sync_middleware2)

    props = {}
    context: Context = cast(Context, {})

    # execute_async() should handle async middleware automatically
    result = await manager.execute_async(Button, props, context)

    # Should execute in priority order: low (-10), async (5), high (10)
    assert execution_order == ["low", "async", "high"]
    assert result is not None
    assert result["low"] is True
    assert result["async"] is True
    assert result["high"] is True


def test_middleware_manager_invalid_middleware():
    """Test that invalid middleware raises TypeError."""
    manager = MiddlewareManager()

    # Object that doesn't satisfy Middleware protocol
    invalid_middleware = {"not": "middleware"}

    with pytest.raises(TypeError, match="does not satisfy Middleware protocol"):
        manager.register_middleware(invalid_middleware)  # type: ignore[arg-type]


def test_middleware_manager_register_service():
    """Test registering middleware as a service with DI."""
    pytest.importorskip("svcs")
    import svcs

    # Create registry and register middleware as service
    registry = svcs.Registry()
    registry.register_factory(DefaultPriorityMiddleware, DefaultPriorityMiddleware)
    container = svcs.Container(registry)

    # Register middleware service
    manager = MiddlewareManager()
    manager.register_middleware_service(DefaultPriorityMiddleware, container)

    props = {"label": "Click"}
    context: Context = cast(Context, {})

    result = manager.execute(Button, props, context)

    assert result is not None
    assert result["label"] == "Click"
    assert result["default"] is True


def test_middleware_manager_service_with_dependencies():
    """Test middleware service with its own dependencies resolved via DI."""
    pytest.importorskip("svcs")
    import svcs

    # Create a middleware that has dependencies
    @dataclass
    class Logger:
        """Simple logger dependency."""

        name: str

    @dataclass
    class LoggingMiddleware:
        """Middleware with logger dependency."""

        logger: Logger
        priority: int = 0

        def __call__(
            self,
            component: type | Callable[..., Any],
            props: dict[str, Any],
            context: Context,
        ) -> dict[str, Any] | None:
            """Log and pass through props."""
            props["logged"] = self.logger.name
            return props

    # Factory function that uses container to get dependencies
    def create_logging_middleware(container: svcs.Container) -> LoggingMiddleware:
        logger = container.get(Logger)
        return LoggingMiddleware(logger=logger)

    # Register logger and middleware as services
    registry = svcs.Registry()
    registry.register_value(Logger, Logger(name="test-logger"))
    # svcs auto-detects takes_container from factory signature
    registry.register_factory(LoggingMiddleware, create_logging_middleware)
    container = svcs.Container(registry)

    # Register middleware service
    manager = MiddlewareManager()
    manager.register_middleware_service(LoggingMiddleware, container)

    props = {}
    context: Context = cast(Context, {})

    result = manager.execute(Button, props, context)

    assert result is not None
    assert result["logged"] == "test-logger"


def test_middleware_manager_mixed_instance_and_service():
    """Test mixing direct instance registration with service registration."""
    pytest.importorskip("svcs")
    import svcs

    # Create registry and register one middleware as service
    registry = svcs.Registry()
    registry.register_factory(HighPriorityMiddleware, HighPriorityMiddleware)
    container = svcs.Container(registry)

    # Register mix of direct instances and services
    execution_order: list[str] = []
    manager = MiddlewareManager()
    manager.register_middleware(LowPriorityMiddleware(executed=execution_order))
    manager.register_middleware_service(HighPriorityMiddleware, container)

    # Also need to set up the execution tracking for the service-created instance
    # This is a bit tricky since the service creates the instance
    # Let's just verify both run

    props = {}
    context: Context = cast(Context, {})

    result = manager.execute(Button, props, context)

    assert result is not None
    assert result["low"] is True
    assert result["high"] is True


def test_middleware_manager_service_invalid_container():
    """Test that invalid container raises TypeError."""
    manager = MiddlewareManager()

    # Object without get() method
    invalid_container = {"not": "container"}

    with pytest.raises(TypeError, match="does not have 'get\\(\\)' method"):
        manager.register_middleware_service(
            DefaultPriorityMiddleware,
            invalid_container,  # type: ignore[arg-type]
        )


def test_middleware_manager_service_resolution_failure():
    """Test that service resolution failure is handled properly."""
    pytest.importorskip("svcs")
    import svcs

    # Create container without registering the middleware
    registry = svcs.Registry()
    container = svcs.Container(registry)

    manager = MiddlewareManager()
    manager.register_middleware_service(DefaultPriorityMiddleware, container)

    props = {}
    context: Context = cast(Context, {})

    # Should raise RuntimeError when trying to resolve unregistered service
    with pytest.raises(RuntimeError, match="Failed to resolve middleware service"):
        manager.execute(Button, props, context)
