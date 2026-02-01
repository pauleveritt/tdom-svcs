"""Middleware with dependencies example.

Demonstrates:
- Middleware as services with their own dependencies
- Using Inject[] for automatic DI resolution
- How scan() discovers both @injectable services and @middleware classes

This example uses Hopscotch patterns (decorators, scanning) for convenience.
You can also use imperative registration with register_middleware() if preferred.
"""

from svcs_di.injectors import HopscotchContainer, HopscotchRegistry

from examples.common import SimpleComponent
from examples.middleware.dependencies import middleware, services
from examples.middleware.dependencies.services import Logger, MetricsCollector
from tdom_svcs import execute_middleware, html, scan


def main() -> str:
    """Execute middleware with injected service dependencies."""
    # Create registry and scan for @injectable and @middleware
    registry = HopscotchRegistry()
    scan(registry, services, middleware)

    with HopscotchContainer(registry) as container:
        # Execute multiple times to see metrics accumulate
        for title in ["Click Me", "Submit", "Cancel"]:
            result = execute_middleware(SimpleComponent, {"title": title}, container)
            assert result is not None

        # Get services to verify they were used
        logger = container.get(Logger)
        metrics = container.get(MetricsCollector)

        # Verify logging middleware used the logger
        assert len(logger.messages) == 3
        assert "Processing SimpleComponent" in logger.messages[0]

        # Verify metrics were recorded
        assert metrics.get_count("SimpleComponent") == 3

        # Render component
        response = html(t"<{SimpleComponent} />", context=container)
        return str(response)


if __name__ == "__main__":
    print(main())
