"""
Middleware with Service Dependencies Example.

This example demonstrates:
1. Middleware as services with their own dependencies
2. Using register_middleware_service() for DI-constructed middleware
3. Factory functions that use svcs.Container to resolve dependencies

This pattern enables:
- Middleware that depend on other services
- Automatic dependency injection for middleware
- Different middleware implementations per environment
"""

from dataclasses import dataclass
from typing import cast

import svcs

from tdom_svcs.services.middleware import Context, MiddlewareManager, setup_container


# Define service dependencies
@dataclass
class Logger:
    """Logger service for middleware to use."""

    name: str

    def info(self, message: str) -> None:
        """Log info message."""
        print(f"[{self.name}] INFO: {message}")

    def error(self, message: str) -> None:
        """Log error message."""
        print(f"[{self.name}] ERROR: {message}")


@dataclass
class MetricsCollector:
    """Metrics service for tracking component usage."""

    def __init__(self):
        self._metrics = {}

    def record(self, component_name: str) -> None:
        """Record component usage."""
        self._metrics[component_name] = self._metrics.get(component_name, 0) + 1
        print(f"[METRICS] Component '{component_name}' used {self._metrics[component_name]} time(s)")


# Define middleware with dependencies
@dataclass
class LoggingMiddleware:
    """Middleware that depends on Logger service."""

    logger: Logger
    priority: int = -10

    def __call__(self, component, props, context):
        """Log component processing using logger service."""
        component_name = (
            component.__name__ if hasattr(component, "__name__") else str(component)
        )
        self.logger.info(f"Processing {component_name}")
        return props


@dataclass
class MetricsMiddleware:
    """Middleware that depends on MetricsCollector service."""

    metrics: MetricsCollector
    priority: int = 0

    def __call__(self, component, props, context):
        """Record component metrics."""
        component_name = (
            component.__name__ if hasattr(component, "__name__") else str(component)
        )
        self.metrics.record(component_name)
        return props


# Example component
class Button:
    """Example component."""

    def __init__(self, title: str):
        self.title = title


def main():
    """Demonstrate middleware with service dependencies."""
    print("=== Middleware with Service Dependencies Example ===\n")

    # 1. Setup: Create registry and register dependency services
    registry = svcs.Registry()

    print("Registering dependency services...")
    registry.register_value(Logger, Logger(name="APP"))
    registry.register_factory(MetricsCollector, MetricsCollector)
    print("✓ Logger and MetricsCollector registered\n")

    # 2. Register middleware services with factory functions
    # Factory functions receive container to resolve dependencies
    def create_logging_middleware(container: svcs.Container) -> LoggingMiddleware:
        """Factory that creates LoggingMiddleware with injected Logger."""
        logger = container.get(Logger)
        return LoggingMiddleware(logger=logger)

    def create_metrics_middleware(container: svcs.Container) -> MetricsMiddleware:
        """Factory that creates MetricsMiddleware with injected MetricsCollector."""
        metrics = container.get(MetricsCollector)
        return MetricsMiddleware(metrics=metrics)

    print("Registering middleware as services...")
    registry.register_factory(LoggingMiddleware, create_logging_middleware)
    registry.register_factory(MetricsMiddleware, create_metrics_middleware)
    print("✓ Middleware registered as services with DI\n")

    # 3. Setup container (registers MiddlewareManager as service by default)
    context: Context = cast(Context, {"config": {"debug": True}})
    setup_container(context, registry)
    print("✓ MiddlewareManager registered\n")

    # 4. Get manager and register middleware services
    container = svcs.Container(registry)
    manager = container.get(MiddlewareManager)

    print("Registering middleware services with manager...")
    manager.register_middleware_service(LoggingMiddleware, container)
    manager.register_middleware_service(MetricsMiddleware, container)
    print("✓ Middleware services registered (will be constructed with DI)\n")

    # 5. Execute middleware chain multiple times
    print("--- Executing with Button component (1st time) ---")
    props = {"title": "Click Me"}
    result = manager.execute(Button, props, context)
    print(f"✓ Result: {result}\n")

    print("--- Executing with Button component (2nd time) ---")
    props = {"title": "Submit"}
    result = manager.execute(Button, props, context)
    print(f"✓ Result: {result}\n")

    print("--- Executing with Button component (3rd time) ---")
    props = {"title": "Cancel"}
    result = manager.execute(Button, props, context)
    print(f"✓ Result: {result}\n")

    print("=== Example Complete ===")
    print("Note: Metrics show Button was used 3 times!")


if __name__ == "__main__":
    main()
