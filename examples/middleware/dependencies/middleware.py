"""Middleware with service dependencies.

Demonstrates:
- Middleware classes with injected service dependencies
- Using factory functions for DI-constructed middleware
- Service-based registration with register_middleware_service
"""

from dataclasses import dataclass
from typing import Any

from examples.middleware.dependencies.services import Logger, MetricsCollector


@dataclass
class LoggingMiddleware:
    """Middleware that depends on Logger service.

    The Logger is injected via a factory function, allowing the
    middleware to use the application's logging infrastructure.
    """

    logger: Logger
    priority: int = -10

    def __call__(
        self, component: type, props: dict[str, Any], context: Any
    ) -> dict[str, Any]:
        component_name = (
            component.__name__ if hasattr(component, "__name__") else str(component)
        )
        self.logger.info(f"Processing {component_name}")
        return props


@dataclass
class MetricsMiddleware:
    """Middleware that depends on MetricsCollector service.

    Records each component processed for usage analytics.
    """

    metrics: MetricsCollector
    priority: int = 0

    def __call__(
        self, component: type, props: dict[str, Any], context: Any
    ) -> dict[str, Any]:
        component_name = (
            component.__name__ if hasattr(component, "__name__") else str(component)
        )
        self.metrics.record(component_name)
        return props
