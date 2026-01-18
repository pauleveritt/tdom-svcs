"""Error handling middleware example.

Demonstrates:
- Catching and handling exceptions in middleware
- Fallback rendering on error
- Circuit breaker pattern for fail-fast behavior
"""

from dataclasses import dataclass, field
from typing import Any, cast

from tdom_svcs.services.middleware import Context, MiddlewareManager


class ValidationError(Exception):
    """Raised when component props fail validation."""

    pass


@dataclass
class ErrorHandlingMiddleware:
    """Middleware that wraps execution with error handling."""

    priority: int = 100
    fallback_props: dict[str, Any] = field(default_factory=dict)
    errors_handled: list = field(default_factory=list)

    def __call__(self, component, props, context):
        try:
            if "invalid" in props:
                raise ValidationError(f"Invalid prop in {component.__name__}")
            return props
        except ValidationError as e:
            self.errors_handled.append(str(e))
            if self.fallback_props:
                return {**props, **self.fallback_props}
            return None


@dataclass
class CircuitBreakerMiddleware:
    """Middleware implementing circuit breaker pattern."""

    priority: int = -10
    failure_threshold: int = 3
    failure_count: int = 0
    circuit_open: bool = False

    def __call__(self, component, props, context):
        if self.circuit_open:
            return None

        if "invalid" in props:
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold:
                self.circuit_open = True
                return None

        return props


class Button:
    """Example component."""

    def __init__(self, title: str, **kwargs):
        self.title = title


def main() -> dict[str, Any]:
    """Demonstrate error handling middleware patterns."""
    manager = MiddlewareManager()

    # Register middleware
    circuit_breaker = CircuitBreakerMiddleware()
    error_handler = ErrorHandlingMiddleware(
        fallback_props={"title": "Error", "variant": "danger"}
    )
    manager.register_middleware(circuit_breaker)
    manager.register_middleware(error_handler)

    context: Context = cast(Context, {"config": {}})

    # Test valid props
    valid_result = manager.execute(Button, {"title": "Click Me"}, context)
    assert valid_result is not None

    # Test invalid props (triggers error handler fallback)
    invalid_result = manager.execute(Button, {"invalid": True}, context)
    assert invalid_result is not None
    assert invalid_result["variant"] == "danger"
    assert len(error_handler.errors_handled) == 1

    # Trigger circuit breaker by exceeding threshold
    for _ in range(2):  # Already had one failure
        manager.execute(Button, {"invalid": True}, context)

    # Circuit should now be open
    assert circuit_breaker.circuit_open is True

    # Valid request fails fast due to open circuit
    blocked_result = manager.execute(Button, {"title": "Submit"}, context)
    assert blocked_result is None

    return {
        "valid_result": valid_result,
        "errors_handled": error_handler.errors_handled,
        "circuit_open": circuit_breaker.circuit_open,
    }


if __name__ == "__main__":
    print(main())
