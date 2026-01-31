"""Middleware with dependencies example.

Demonstrates:
- Middleware as services with their own dependencies
- Using register_middleware_service() for DI-constructed middleware
- Factory functions that resolve dependencies from container
- Testing with fakes (site overrides Logger with FakeLogger)
"""

from typing import cast

import svcs

from svcs_di.injectors import HopscotchContainer, HopscotchRegistry
from svcs_di.injectors.scanning import scan

from examples.common import Greeting, Request
from examples.middleware.dependencies import components, services, site
from examples.middleware.dependencies.middleware import LoggingMiddleware, MetricsMiddleware
from examples.middleware.dependencies.services import Logger, MetricsCollector
from tdom_svcs import html
from tdom_svcs.services.middleware import Context, MiddlewareManager, setup_container


def main() -> str:
    """Execute middleware with injected service dependencies."""
    registry = HopscotchRegistry()
    scan(registry, services, components)

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

    # Scan the site (this overrides Logger with FakeLogger)
    scan(registry, site)

    # Setup middleware manager
    context: Context = cast(Context, {"config": {"debug": True}})
    setup_container(context, registry)

    with HopscotchContainer(registry) as container:
        container.register_local_value(Request, Request(user_id="1"))

        # Get the middleware manager
        manager = container.get(MiddlewareManager)

        # Register middleware services (uses factory functions for DI)
        manager.register_middleware_service(LoggingMiddleware, container)
        manager.register_middleware_service(MetricsMiddleware, container)

        # Execute multiple times to see metrics accumulate
        for title in ["Click Me", "Submit", "Cancel"]:
            result = manager.execute(Greeting, {"title": title}, context)
            assert result is not None

        # Get the actual logger (might be FakeLogger from site)
        actual_logger = container.get(Logger)

        # Verify the site's FakeLogger was used
        assert type(actual_logger).__name__ == "FakeLogger"
        assert len(actual_logger.messages) == 3

        # Verify metrics were recorded
        assert metrics.get_count("Greeting") == 3

        # Render Greeting component
        response = html(t"<{Greeting} />", context=container)
        result_html = str(response)

        assert "Hello Alice!" in result_html

        return result_html


if __name__ == "__main__":
    print(main())
