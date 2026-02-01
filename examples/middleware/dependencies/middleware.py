"""Middleware with service dependencies.

Demonstrates:
- Middleware classes with injected service dependencies
- Using Inject[] for automatic DI resolution
- The @middleware decorator for discovery
"""

from dataclasses import dataclass

from svcs_di import Inject

from tdom_svcs import middleware
from tdom_svcs.types import Component, Context, Props, PropsResult

from examples.middleware.dependencies.services import Logger, MetricsCollector


# Middleware can have container dependencies
@middleware
@dataclass
class LoggingMiddleware:
    """Middleware that depends on Logger service.

    The Logger is injected automatically via Inject[], allowing the
    middleware to use the application's logging infrastructure.
    """

    logger: Inject[Logger]
    priority: int = -10

    def __call__(
        self, component: Component, props: Props, context: Context
    ) -> PropsResult:
        component_name = getattr(component, "__name__", type(component).__name__)
        self.logger.info(f"Processing {component_name}")
        return props


@middleware
@dataclass
class MetricsMiddleware:
    """Middleware that depends on MetricsCollector service.

    Records each component processed for usage analytics.
    """

    metrics: Inject[MetricsCollector]
    priority: int = 0

    def __call__(
        self, component: Component, props: Props, context: Context
    ) -> PropsResult:
        component_name = getattr(component, "__name__", type(component).__name__)
        self.metrics.record(component_name)
        return props
