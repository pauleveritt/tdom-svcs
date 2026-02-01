"""Error handling middleware example.

Demonstrates:
- Catching and handling exceptions in middleware
- Fallback rendering on error
- Circuit breaker pattern for fail-fast behavior

This example uses Hopscotch patterns (decorators, scanning) for convenience.
You can also use imperative registration with register_middleware() if preferred.
"""

from svcs_di.injectors import HopscotchContainer, HopscotchRegistry

from examples.common import SimpleComponent
from examples.middleware.error_handling import middleware
from examples.middleware.error_handling.middleware import (
    CircuitBreakerMiddleware,
    ErrorHandlingMiddleware,
    FallbackMiddleware,
)
from tdom_svcs import execute_middleware, html, scan


def main() -> str:
    """Demonstrate error handling middleware patterns."""
    # Create registry and scan for @injectable services and @middleware
    registry = HopscotchRegistry()
    scan(registry, middleware)

    with HopscotchContainer(registry) as container:
        # Get middleware instances from container to assert later
        circuit_breaker = container.get(CircuitBreakerMiddleware)
        fallback = container.get(FallbackMiddleware)
        error_handler = container.get(ErrorHandlingMiddleware)

        # Configure middleware with specific settings
        fallback.defaults = {"variant": "secondary"}
        error_handler.fallback_props = {"title": "Error", "variant": "danger"}

        # Test 1: Valid props pass through all middleware
        valid_result = execute_middleware(
            SimpleComponent, {"title": "Click Me"}, container
        )
        assert valid_result is not None
        assert valid_result["title"] == "Click Me"
        assert valid_result["variant"] == "secondary"  # From FallbackMiddleware

        # Test 2: Invalid props trigger error handler
        invalid_result = execute_middleware(
            SimpleComponent, {"invalid": True}, container
        )
        assert invalid_result is not None
        assert invalid_result["variant"] == "danger"  # From ErrorHandlingMiddleware
        assert len(error_handler.errors_handled) == 1

        # Test 3: Multiple failures trigger circuit breaker
        for _ in range(2):  # Already had one failure
            execute_middleware(SimpleComponent, {"invalid": True}, container)

        assert circuit_breaker.circuit_open is True

        # Test 4: Open circuit blocks all requests
        blocked_result = execute_middleware(
            SimpleComponent, {"title": "Submit"}, container
        )
        assert blocked_result is None

        # Test 5: Reset circuit allows recovery
        circuit_breaker.reset()
        recovered_result = execute_middleware(
            SimpleComponent, {"title": "Recovered"}, container
        )
        assert recovered_result is not None

        # Render component
        response = html(t"<{SimpleComponent} />", context=container)
        return str(response)


if __name__ == "__main__":
    print(main())
