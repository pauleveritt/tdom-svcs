"""Testing middleware with fakes example.

Demonstrates the recommended testing pattern:
- Create simple fakes that implement the required interface
- Register fakes in test registry instead of real services
- Test middleware behavior in isolation
- No mock framework needed
"""

from dataclasses import dataclass, field
from typing import cast

import svcs

from svcs_di import HopscotchContainer, HopscotchRegistry

from tdom_svcs.services.middleware import Context, MiddlewareManager, setup_container


@dataclass
class Logger:
    """Production logger service."""

    name: str
    _logs: list[str] = field(default_factory=list, repr=False)

    def info(self, message: str) -> None:
        self._logs.append(f"INFO: {message}")


@dataclass
class FakeLogger:
    """Fake logger for testing - captures messages without side effects."""

    name: str
    _logs: list[str] = field(default_factory=list, repr=False)

    def info(self, message: str) -> None:
        self._logs.append(f"INFO: {message}")

    def get_logs(self) -> list[str]:
        return self._logs.copy()


@dataclass
class LoggingMiddleware:
    """Middleware that depends on Logger service."""

    logger: Logger
    priority: int = 0

    def __call__(self, component, props, context):
        component_name = component.__name__
        self.logger.info(f"Processing {component_name}")
        return props


class Button:
    """Test component."""

    def __init__(self, title: str):
        self.title = title


def main() -> list[str]:
    """Test middleware using fake logger."""
    registry = HopscotchRegistry()

    # Register fake logger instead of real logger
    fake_logger = FakeLogger(name="TEST")
    registry.register_value(Logger, fake_logger)

    # Register middleware that will use fake
    def create_logging_middleware(container: svcs.Container) -> LoggingMiddleware:
        return LoggingMiddleware(logger=container.get(Logger))

    registry.register_factory(LoggingMiddleware, create_logging_middleware)

    # Setup container
    context: Context = cast(Context, {"config": {}})
    setup_container(context, registry)

    with HopscotchContainer(registry) as container:
        manager = container.get(MiddlewareManager)
        manager.register_middleware_service(LoggingMiddleware, container)

        # Execute middleware
        props = {"title": "Click Me"}
        result = manager.execute(Button, props, context)

        # Verify using fake's captured data
        logs = fake_logger.get_logs()

        assert len(logs) == 1
        assert "Processing Button" in logs[0]
        assert result is not None
        assert result["title"] == "Click Me"

        return logs


if __name__ == "__main__":
    print(main())
