"""
Tests for Middleware Protocol.

This module tests the Middleware protocol which defines the interface for
middleware implementations that wrap component lifecycle phases.
"""

from dataclasses import dataclass
from typing import Any, Callable, cast


from tdom_svcs.services.middleware import Context, Middleware


# Test fixtures - middleware implementations


@dataclass
class SimpleMiddleware:
    """Simple middleware implementation for testing."""

    priority: int = 0

    def __call__(
        self,
        component: type | Callable[..., Any],
        props: dict[str, Any],
        context: Context,
    ) -> dict[str, Any] | None:
        """Execute middleware - just return props unchanged."""
        return props


@dataclass
class TransformingMiddleware:
    """Middleware that transforms props."""

    priority: int = 10

    def __call__(
        self,
        component: type | Callable[..., Any],
        props: dict[str, Any],
        context: Context,
    ) -> dict[str, Any] | None:
        """Add a timestamp to props."""
        props["timestamp"] = "2025-12-29"
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

    priority: int = 0

    async def __call__(
        self,
        component: type | Callable[..., Any],
        props: dict[str, Any],
        context: Context,
    ) -> dict[str, Any] | None:
        """Async middleware execution."""
        return props


class Button:
    """Test class component."""

    def __init__(self, label: str = "Click"):
        self.label = label


def heading(text: str = "Heading") -> str:
    """Test function component."""
    return f"<h1>{text}</h1>"


def test_protocol_satisfaction_with_dataclass():
    """Test that dataclass middleware satisfies Middleware protocol."""
    middleware = SimpleMiddleware(priority=5)

    # Check protocol satisfaction
    assert isinstance(middleware, Middleware)
    assert middleware.priority == 5


def test_protocol_satisfaction_with_class():
    """Test that class-based middleware satisfies Middleware protocol."""

    class LoggingMiddleware:
        def __init__(self):
            self.priority = -10

        def __call__(
            self,
            component: type | Callable[..., Any],
            props: dict[str, Any],
            context: Context,
        ) -> dict[str, Any] | None:
            return props

    middleware = LoggingMiddleware()
    assert isinstance(middleware, Middleware)


def test_middleware_with_class_component():
    """Test middleware execution with class component."""
    middleware = SimpleMiddleware()
    component = Button
    props = {"label": "Submit"}
    # Plain dict satisfies Context protocol at runtime
    context: Context = cast(Context, {"logger": "test_logger"})

    result = middleware(component, props, context)

    assert result is props
    assert isinstance(component, type)  # Class components are types


def test_middleware_with_function_component():
    """Test middleware execution with function component."""
    middleware = SimpleMiddleware()
    component = heading
    props = {"text": "Welcome"}
    # Plain dict satisfies Context protocol at runtime
    context: Context = cast(Context, {"logger": "test_logger"})

    result = middleware(component, props, context)

    assert result is props
    assert not isinstance(component, type)  # Function components are not types


def test_middleware_props_transformation():
    """Test middleware can transform props."""
    middleware = TransformingMiddleware()
    component = Button
    props = {"label": "Click"}
    # Plain dict satisfies Context protocol at runtime
    context: Context = cast(Context, {})

    result = middleware(component, props, context)

    assert result is not None
    assert result["label"] == "Click"
    assert result["timestamp"] == "2025-12-29"


def test_middleware_halt_execution():
    """Test middleware can halt execution by returning None."""
    middleware = HaltingMiddleware()
    component = Button
    props = {"label": "Click"}
    # Plain dict satisfies Context protocol at runtime
    context: Context = cast(Context, {})

    result = middleware(component, props, context)

    assert result is None


def test_middleware_priority_ordering():
    """Test middleware priority attribute for ordering."""
    low_priority = SimpleMiddleware(priority=-10)
    default_priority = SimpleMiddleware(priority=0)
    high_priority = SimpleMiddleware(priority=10)

    # Lower priority executes first
    assert low_priority.priority < default_priority.priority
    assert default_priority.priority < high_priority.priority

    # Sort by priority
    middlewares = [high_priority, low_priority, default_priority]
    sorted_middlewares = sorted(middlewares, key=lambda m: m.priority)

    assert sorted_middlewares[0] is low_priority
    assert sorted_middlewares[1] is default_priority
    assert sorted_middlewares[2] is high_priority


def test_async_middleware_protocol_satisfaction():
    """Test that async middleware satisfies Middleware protocol."""
    middleware = AsyncMiddleware()

    assert isinstance(middleware, Middleware)
    assert middleware.priority == 0
