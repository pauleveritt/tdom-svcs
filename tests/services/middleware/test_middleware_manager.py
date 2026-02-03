"""
Tests for middleware registration and execution module.

This module tests the module-level functions for middleware management:
- register_middleware() - Register middleware types with registry
- execute_middleware() - Execute middleware chain synchronously
- execute_middleware_async() - Execute middleware chain with async support
"""

from dataclasses import dataclass
from typing import Any, Callable

import pytest
import svcs

from tdom_svcs import (
    execute_middleware,
    execute_middleware_async,
    register_middleware,
)
from tdom_svcs.services.middleware import Context

from ...conftest import (
    AsyncMiddleware,
    DefaultPriorityMiddleware,
    HaltingMiddleware,
    HighPriorityMiddleware,
    LowPriorityMiddleware,
)


class Button:
    """Test class component."""

    def __init__(self, label: str = "Click"):
        self.label = label


def heading(text: str = "Heading") -> str:
    """Test function component."""
    return f"<h1>{text}</h1>"


class TestRegisterAndExecute:
    """Tests for basic middleware registration and execution."""

    def test_register_and_execute(self, registry, container):
        """Test registering middleware and basic execution."""
        # Register middleware type
        registry.register_factory(DefaultPriorityMiddleware, DefaultPriorityMiddleware)
        register_middleware(registry, DefaultPriorityMiddleware)

        props = {"label": "Click"}

        result = execute_middleware(Button, props, container)

        assert result is not None
        assert result["label"] == "Click"
        assert result["default"] is True

    def test_priority_ordering(self, registry, container):
        """Test middleware executes in priority order (lower numbers first)."""
        # Register middleware types
        registry.register_factory(HighPriorityMiddleware, HighPriorityMiddleware)
        registry.register_factory(LowPriorityMiddleware, LowPriorityMiddleware)
        registry.register_factory(DefaultPriorityMiddleware, DefaultPriorityMiddleware)

        # Register in random order - should still execute in priority order
        register_middleware(registry, HighPriorityMiddleware)
        register_middleware(registry, LowPriorityMiddleware)
        register_middleware(registry, DefaultPriorityMiddleware)

        props = {}

        result = execute_middleware(Button, props, container)

        # Should execute in priority order: low (-10), default (0), high (10)
        assert result is not None
        assert result["_execution_order"] == ["low", "default", "high"]
        assert result["low"] is True
        assert result["default"] is True
        assert result["high"] is True

    def test_halt_on_none(self, registry, container):
        """Test execution halts when middleware returns None."""
        registry.register_factory(
            LowPriorityMiddleware, lambda: LowPriorityMiddleware(priority=-10)
        )
        registry.register_factory(
            HaltingMiddleware, lambda: HaltingMiddleware(priority=0)
        )
        registry.register_factory(
            HighPriorityMiddleware, lambda: HighPriorityMiddleware(priority=10)
        )

        register_middleware(registry, LowPriorityMiddleware)
        register_middleware(registry, HaltingMiddleware)
        register_middleware(registry, HighPriorityMiddleware)

        props = {}

        result = execute_middleware(Button, props, container)

        # Execution should halt at halting middleware
        # Low priority runs, halting runs and returns None, high never runs
        assert result is None
        assert "low" in props
        assert props["_execution_order"] == ["low"]
        assert "high" not in props


class TestComponentTypes:
    """Tests for different component types."""

    def test_with_function_component(self, registry, container):
        """Test middleware execution with function component."""
        registry.register_factory(DefaultPriorityMiddleware, DefaultPriorityMiddleware)
        register_middleware(registry, DefaultPriorityMiddleware)

        props = {"text": "Welcome"}

        result = execute_middleware(heading, props, container)

        assert result is not None
        assert result["text"] == "Welcome"
        assert result["default"] is True
        # Verify it's a function component
        assert not isinstance(heading, type)

    def test_with_class_component(self, registry, container):
        """Test middleware execution with class component."""
        registry.register_factory(DefaultPriorityMiddleware, DefaultPriorityMiddleware)
        register_middleware(registry, DefaultPriorityMiddleware)

        props = {"label": "Submit"}

        result = execute_middleware(Button, props, container)

        assert result is not None
        assert result["label"] == "Submit"
        assert result["default"] is True
        # Verify it's a class component
        assert isinstance(Button, type)


class TestAsyncMiddleware:
    """Tests for async middleware support."""

    @pytest.mark.anyio
    async def test_async_middleware(self, registry, container):
        """Test execution with async middleware using anyio."""
        registry.register_factory(
            LowPriorityMiddleware, lambda: LowPriorityMiddleware(priority=-10)
        )
        registry.register_factory(AsyncMiddleware, lambda: AsyncMiddleware(priority=5))
        registry.register_factory(
            HighPriorityMiddleware, lambda: HighPriorityMiddleware(priority=10)
        )

        register_middleware(registry, LowPriorityMiddleware)
        register_middleware(registry, AsyncMiddleware)
        register_middleware(registry, HighPriorityMiddleware)

        props = {}

        # execute_middleware_async() should handle async middleware automatically
        result = await execute_middleware_async(Button, props, container)

        # Should execute in priority order: low (-10), async (5), high (10)
        assert result is not None
        assert result["_execution_order"] == ["low", "async", "high"]
        assert result["low"] is True
        assert result["async"] is True
        assert result["high"] is True


class TestDependencyInjection:
    """Tests for middleware with DI dependencies."""

    def test_middleware_with_dependencies(self, registry, container):
        """Test middleware with its own dependencies resolved via DI."""

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
        def create_logging_middleware(cont: svcs.Container) -> LoggingMiddleware:
            logger = cont.get(Logger)
            return LoggingMiddleware(logger=logger)

        # Register logger and middleware as services
        registry.register_value(Logger, Logger(name="test-logger"))
        registry.register_factory(LoggingMiddleware, create_logging_middleware)

        # Register middleware type
        register_middleware(registry, LoggingMiddleware)

        props = {}

        result = execute_middleware(Button, props, container)

        assert result is not None
        assert result["logged"] == "test-logger"

    def test_mixed_registration(self, registry, container):
        """Test mixing different middleware types."""
        # Register middleware types
        registry.register_factory(LowPriorityMiddleware, LowPriorityMiddleware)
        registry.register_factory(HighPriorityMiddleware, HighPriorityMiddleware)

        register_middleware(registry, LowPriorityMiddleware)
        register_middleware(registry, HighPriorityMiddleware)

        props = {}

        result = execute_middleware(Button, props, container)

        assert result is not None
        assert result["_execution_order"] == ["low", "high"]
        assert result["low"] is True
        assert result["high"] is True


class TestErrorHandling:
    """Tests for error handling."""

    def test_async_in_sync_raises_error(self, registry, container):
        """Test that async middleware in sync execution raises RuntimeError."""
        registry.register_factory(AsyncMiddleware, AsyncMiddleware)
        register_middleware(registry, AsyncMiddleware)

        props = {}

        with pytest.raises(
            RuntimeError, match="Async middleware.*detected in synchronous execution"
        ):
            execute_middleware(Button, props, container)
