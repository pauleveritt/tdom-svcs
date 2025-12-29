"""
Testing Middleware with Fakes Example.

This example demonstrates the recommended testing pattern:
1. Create simple fakes that implement the required interface
2. Register fakes in test registry instead of real services
3. Test middleware behavior in isolation
4. No mock framework needed

This pattern follows svcs best practices:
- Use fakes, not mocks
- Simple and predictable test doubles
- Tests are resilient to refactoring
"""

from dataclasses import dataclass, field
from typing import cast

import svcs

from tdom_svcs.services.middleware import Context, MiddlewareManager, setup_container


# Production service
@dataclass
class Logger:
    """Production logger service."""

    name: str
    _logs: list[str] = field(default_factory=list, repr=False)

    def info(self, message: str) -> None:
        """Log info message."""
        self._logs.append(f"INFO: {message}")
        print(f"[{self.name}] {message}")


# Fake for testing
@dataclass
class FakeLogger:
    """Fake logger for testing - captures messages without side effects."""

    name: str
    _logs: list[str] = field(default_factory=list, repr=False)

    def info(self, message: str) -> None:
        """Record info message without printing."""
        self._logs.append(f"INFO: {message}")

    def get_logs(self) -> list[str]:
        """Get captured log messages (testing utility)."""
        return self._logs.copy()


# Middleware that uses Logger
@dataclass
class LoggingMiddleware:
    """Middleware that depends on Logger service."""

    logger: Logger
    priority: int = 0

    def __call__(self, component, props, context):
        """Log component processing."""
        component_name = (
            component.__name__ if hasattr(component, "__name__") else str(component)
        )
        self.logger.info(f"Processing {component_name}")
        return props


# Component for testing
class Button:
    """Test component."""

    def __init__(self, title: str):
        self.title = title


def test_middleware_with_fake_logger():
    """Test middleware using fake logger - no mocks needed!"""
    print("=== Testing Middleware with Fake Logger ===\n")

    # 1. Create test registry
    registry = svcs.Registry()

    # 2. Register fake logger (not real logger)
    print("Registering fake logger...")
    fake_logger = FakeLogger(name="TEST")
    registry.register_value(Logger, fake_logger)
    print("✓ Fake logger registered\n")

    # 3. Register middleware service that will use fake
    def create_logging_middleware(container: svcs.Container) -> LoggingMiddleware:
        logger = container.get(Logger)  # Gets fake logger
        return LoggingMiddleware(logger=logger)

    registry.register_factory(LoggingMiddleware, create_logging_middleware)

    # 4. Setup container and get manager
    context: Context = cast(Context, {"config": {}})
    setup_container(context, registry)

    container = svcs.Container(registry)
    manager = container.get(MiddlewareManager)

    # 5. Register middleware service
    print("Registering middleware service...")
    manager.register_middleware_service(LoggingMiddleware, container)
    print("✓ Middleware registered\n")

    # 6. Execute middleware
    print("Executing middleware...")
    props = {"title": "Click Me"}
    result = manager.execute(Button, props, context)
    print("✓ Middleware executed\n")

    # 7. Verify using fake's captured data (no mock assertions!)
    logs = fake_logger.get_logs()
    print(f"Captured logs: {logs}")

    # Simple assertions on captured data
    assert len(logs) == 1, f"Expected 1 log entry, got {len(logs)}"
    assert "Processing Button" in logs[0], f"Expected log about Button, got {logs[0]}"
    assert result is not None, "Middleware should not halt execution"
    assert result["title"] == "Click Me", "Props should pass through unchanged"

    print("\n✓ All assertions passed!")
    print("\n=== Test Complete ===")
    print("\nKey insights:")
    print("• Fake logger is simple and predictable")
    print("• No mock framework needed")
    print("• Tests are easy to understand and maintain")
    print("• Fake can be reused across multiple tests")


def test_middleware_direct_injection():
    """Test middleware by injecting fake directly - even simpler!"""
    print("\n\n=== Testing with Direct Injection (No Container) ===\n")

    # Create fake logger
    fake_logger = FakeLogger(name="TEST")

    # Create middleware directly with fake (type checker doesn't know fake implements protocol)
    middleware = LoggingMiddleware(logger=fake_logger)  # type: ignore[arg-type]

    # Create manager and register middleware instance
    manager = MiddlewareManager()
    manager.register_middleware(middleware)

    # Execute
    context: Context = cast(Context, {})
    props = {"title": "Submit"}
    result = manager.execute(Button, props, context)

    # Verify
    logs = fake_logger.get_logs()
    assert len(logs) == 1
    assert "Processing Button" in logs[0]

    print(f"✓ Captured logs: {logs}")
    print("✓ Test passed!\n")
    print("Key insight: When possible, inject fakes directly without container")


if __name__ == "__main__":
    # Run both test patterns
    test_middleware_with_fake_logger()
    test_middleware_direct_injection()
