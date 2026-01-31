"""Error handling middleware example.

Demonstrates:
- Catching and handling exceptions in middleware
- Fallback rendering on error
- Circuit breaker pattern for fail-fast behavior
"""

from typing import cast

from svcs_di.injectors import HopscotchContainer, HopscotchRegistry
from svcs_di.injectors.scanning import scan

from examples.common import Greeting, Request
from examples.middleware.error_handling import components, services
from examples.middleware.error_handling.middleware import (
    CircuitBreakerMiddleware,
    ErrorHandlingMiddleware,
    FallbackMiddleware,
)
from tdom_svcs import html
from tdom_svcs.services.middleware import Context, MiddlewareManager, setup_container


def main() -> str:
    """Demonstrate error handling middleware patterns."""
    registry = HopscotchRegistry()
    scan(registry, services, components)

    # Setup middleware manager
    context: Context = cast(Context, {"config": {"debug": True}})
    setup_container(context, registry)

    with HopscotchContainer(registry) as container:
        container.register_local_value(Request, Request(user_id="1"))

        manager = container.get(MiddlewareManager)

        # Register middleware
        circuit_breaker = CircuitBreakerMiddleware()
        fallback = FallbackMiddleware(defaults={"variant": "secondary"})
        error_handler = ErrorHandlingMiddleware(
            fallback_props={"title": "Error", "variant": "danger"}
        )

        manager.register_middleware(circuit_breaker)
        manager.register_middleware(fallback)
        manager.register_middleware(error_handler)

        # Test 1: Valid props
        valid_result = manager.execute(Greeting, {"title": "Click Me"}, context)
        assert valid_result is not None
        assert valid_result["title"] == "Click Me"
        # Fallback should have added default variant
        assert valid_result["variant"] == "secondary"

        # Test 2: Invalid props (triggers error handler)
        invalid_result = manager.execute(Greeting, {"invalid": True}, context)
        assert invalid_result is not None
        # Error handler should have added fallback props
        assert invalid_result["variant"] == "danger"
        assert len(error_handler.errors_handled) == 1

        # Test 3: Trigger circuit breaker
        # Send more invalid requests to trigger circuit breaker
        for _ in range(2):  # Already had one failure
            manager.execute(Greeting, {"invalid": True}, context)

        # Circuit should now be open
        assert circuit_breaker.circuit_open is True

        # Test 4: Valid request blocked by open circuit
        blocked_result = manager.execute(Greeting, {"title": "Submit"}, context)
        assert blocked_result is None

        # Test 5: Reset circuit and try again
        circuit_breaker.reset()
        recovered_result = manager.execute(Greeting, {"title": "Recovered"}, context)
        assert recovered_result is not None

        # Render Greeting component
        response = html(t"<{Greeting} />", context=container)
        result_html = str(response)

        assert "Hello Alice!" in result_html

        return result_html


if __name__ == "__main__":
    print(main())
