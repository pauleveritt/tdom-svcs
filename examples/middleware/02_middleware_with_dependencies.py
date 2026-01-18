"""Middleware with service dependencies example.

Demonstrates:
- Middleware as services with their own dependencies
- Using register_middleware_service() for DI-constructed middleware
- Factory functions that resolve dependencies from container
"""

from dataclasses import dataclass, field
from typing import Any, cast

import svcs

from svcs_di import HopscotchContainer, HopscotchRegistry

from tdom_svcs.services.middleware import Context, MiddlewareManager, setup_container


@dataclass
class Logger:
    """Logger service for middleware to use."""

    name: str
    messages: list = field(default_factory=list)

    def info(self, message: str) -> None:
        self.messages.append(message)


@dataclass
class MetricsCollector:
    """Metrics service for tracking component usage."""

    _metrics: dict = field(default_factory=dict)

    def record(self, component_name: str) -> None:
        self._metrics[component_name] = self._metrics.get(component_name, 0) + 1

    def get_count(self, component_name: str) -> int:
        return self._metrics.get(component_name, 0)


@dataclass
class LoggingMiddleware:
    """Middleware that depends on Logger service."""

    logger: Logger
    priority: int = -10

    def __call__(self, component, props, context):
        component_name = component.__name__
        self.logger.info(f"Processing {component_name}")
        return props


@dataclass
class MetricsMiddleware:
    """Middleware that depends on MetricsCollector service."""

    metrics: MetricsCollector
    priority: int = 0

    def __call__(self, component, props, context):
        component_name = component.__name__
        self.metrics.record(component_name)
        return props


class Button:
    """Example component."""

    def __init__(self, title: str):
        self.title = title


def main() -> dict[str, Any]:
    """Execute middleware with injected service dependencies."""
    registry = HopscotchRegistry()

    # Register dependency services
    logger = Logger(name="APP")
    metrics = MetricsCollector()
    registry.register_value(Logger, logger)
    registry.register_value(MetricsCollector, metrics)

    # Register middleware with factory functions
    def create_logging_middleware(container: svcs.Container) -> LoggingMiddleware:
        return LoggingMiddleware(logger=container.get(Logger))

    def create_metrics_middleware(container: svcs.Container) -> MetricsMiddleware:
        return MetricsMiddleware(metrics=container.get(MetricsCollector))

    registry.register_factory(LoggingMiddleware, create_logging_middleware)
    registry.register_factory(MetricsMiddleware, create_metrics_middleware)

    # Setup container
    context: Context = cast(Context, {"config": {"debug": True}})
    setup_container(context, registry)

    with HopscotchContainer(registry) as container:
        manager = container.get(MiddlewareManager)

        # Register middleware services
        manager.register_middleware_service(LoggingMiddleware, container)
        manager.register_middleware_service(MetricsMiddleware, container)

        # Execute multiple times
        for title in ["Click Me", "Submit", "Cancel"]:
            result = manager.execute(Button, {"title": title}, context)
            assert result is not None

        # Verify metrics were recorded
        assert metrics.get_count("Button") == 3
        assert len(logger.messages) == 3

        return {"button_count": metrics.get_count("Button")}


if __name__ == "__main__":
    print(main())
