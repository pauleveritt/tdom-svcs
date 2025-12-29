"""
Error Handling Middleware Example.

This example demonstrates:
1. Catching and handling exceptions in middleware
2. Wrapping component execution with try/except
3. Fallback rendering on error
4. Error recovery patterns
5. Async error handling

Error handling middleware provides a safety net for component rendering,
allowing graceful degradation instead of application crashes.
"""

from dataclasses import dataclass
from typing import Any, Callable, cast

from tdom_svcs.services.middleware import Context, Middleware, MiddlewareManager


# Custom exceptions for demonstration
class ValidationError(Exception):
    """Raised when component props fail validation."""

    pass


class RenderingError(Exception):
    """Raised when component rendering fails."""

    pass


# Error handling middleware
@dataclass
class ErrorHandlingMiddleware:
    """
    Middleware that wraps execution with error handling.

    This middleware catches exceptions from downstream middleware or components
    and provides fallback behavior instead of propagating the exception.

    Priority is typically high (runs late) to catch errors from earlier middleware.
    """

    priority: int = 100  # Run late to catch errors from other middleware
    fallback_props: dict[str, Any] | None = None

    def __call__(
        self,
        component: type | Callable[..., Any],
        props: dict[str, Any],
        context: Context,
    ) -> dict[str, Any] | None:
        """
        Execute with error handling.

        Catches exceptions and either returns fallback props or halts execution
        depending on the error type and configuration.
        """
        component_name = (
            component.__name__ if hasattr(component, "__name__") else str(component)
        )

        try:
            # In real implementation, this would wrap the entire middleware chain
            # For demo purposes, we just validate props here
            if "invalid" in props:
                raise ValidationError(f"Invalid prop in {component_name}")

            print(f"[ERROR-HANDLER] No errors for {component_name}")
            return props

        except ValidationError as e:
            # Validation errors can be recovered with fallback
            print(f"[ERROR-HANDLER] Caught validation error: {e}")
            print(f"[ERROR-HANDLER] Using fallback props")

            if self.fallback_props:
                # Return fallback props to allow rendering to continue
                return {**props, **self.fallback_props}
            else:
                # No fallback available - halt execution
                print(f"[ERROR-HANDLER] No fallback available - halting")
                return None

        except Exception as e:
            # Unknown errors should halt execution
            print(f"[ERROR-HANDLER] Caught unexpected error: {e}")
            print(f"[ERROR-HANDLER] Halting execution for safety")
            return None


# Error logging middleware
@dataclass
class ErrorLoggingMiddleware:
    """
    Middleware that logs errors without stopping execution.

    This runs early to detect problems but allows execution to continue
    so other middleware can handle recovery.
    """

    priority: int = -5  # Run early to detect issues

    def __call__(
        self,
        component: type | Callable[..., Any],
        props: dict[str, Any],
        context: Context,
    ) -> dict[str, Any] | None:
        """Log suspicious props but continue execution."""
        component_name = (
            component.__name__ if hasattr(component, "__name__") else str(component)
        )

        # Check for suspicious patterns
        suspicious_keys = ["invalid", "error", "bad"]
        found = [key for key in suspicious_keys if key in props]

        if found:
            print(
                f"[ERROR-LOG] Warning: {component_name} has suspicious props: {found}"
            )
            # Log but don't halt - let error handler deal with it
            print(f"[ERROR-LOG] Continuing execution...")

        return props


# Circuit breaker middleware (advanced pattern)
@dataclass
class CircuitBreakerMiddleware:
    """
    Middleware that implements circuit breaker pattern.

    After a certain number of failures, the circuit "opens" and subsequent
    requests fail fast without attempting execution.
    """

    priority: int = -10  # Run very early
    failure_threshold: int = 3
    _failure_count: int = 0
    _circuit_open: bool = False

    def __call__(
        self,
        component: type | Callable[..., Any],
        props: dict[str, Any],
        context: Context,
    ) -> dict[str, Any] | None:
        """Check circuit breaker state before allowing execution."""
        component_name = (
            component.__name__ if hasattr(component, "__name__") else str(component)
        )

        # Check if circuit is open
        if self._circuit_open:
            print(
                f"[CIRCUIT-BREAKER] Circuit open for {component_name} - failing fast"
            )
            return None

        # Check for failure indicators
        if "invalid" in props or "error" in props:
            self._failure_count += 1
            print(
                f"[CIRCUIT-BREAKER] Failure detected ({self._failure_count}/{self.failure_threshold})"
            )

            if self._failure_count >= self.failure_threshold:
                self._circuit_open = True
                print(f"[CIRCUIT-BREAKER] Opening circuit - too many failures")
                return None

        return props


# Example components
class Button:
    """Example component."""

    def __init__(self, title: str, **kwargs):
        self.title = title
        self.props = kwargs


class Card:
    """Example component."""

    def __init__(self, title: str, content: str, **kwargs):
        self.title = title
        self.content = content
        self.props = kwargs


def main():
    """Demonstrate error handling middleware patterns."""
    print("=== Error Handling Middleware Example ===\n")

    # Create manager
    manager = MiddlewareManager()

    # Register middleware in priority order
    print("Registering middleware...")
    manager.register_middleware(CircuitBreakerMiddleware())
    manager.register_middleware(ErrorLoggingMiddleware())
    manager.register_middleware(
        ErrorHandlingMiddleware(fallback_props={"title": "Error", "variant": "danger"})
    )
    print("Registered: CircuitBreakerMiddleware (-10)")
    print("            ErrorLoggingMiddleware (-5)")
    print("            ErrorHandlingMiddleware (100)")
    print()

    # Create context
    context: Context = cast(Context, {"config": {}})

    # Test 1: Valid props (no errors)
    print("--- Test 1: Valid props ---")
    props = {"title": "Click Me", "variant": "primary"}
    result = manager.execute(Button, props, context)
    print(f"Result: {result}\n")

    # Test 2: Invalid props (validation error with recovery)
    print("--- Test 2: Invalid props (with fallback recovery) ---")
    props = {"invalid": True, "variant": "primary"}
    result = manager.execute(Button, props, context)
    print(f"Result: {result}\n")

    # Test 3: Another invalid request (circuit breaker counting)
    print("--- Test 3: Second invalid request ---")
    props = {"invalid": True, "variant": "secondary"}
    result = manager.execute(Button, props, context)
    print(f"Result: {result}\n")

    # Test 4: Third invalid request (circuit breaker opens)
    print("--- Test 4: Third invalid request (circuit opens) ---")
    props = {"invalid": True, "variant": "danger"}
    result = manager.execute(Button, props, context)
    print(f"Result: {result}\n")

    # Test 5: Valid props but circuit is open
    print("--- Test 5: Valid props (but circuit is open) ---")
    props = {"title": "Submit", "variant": "primary"}
    result = manager.execute(Button, props, context)
    print(f"Result: {result}\n")

    print("=== Example Complete ===\n")
    print("Key patterns demonstrated:")
    print("1. Error handling with fallback props")
    print("2. Error logging that doesn't halt execution")
    print("3. Circuit breaker pattern for fail-fast behavior")
    print("4. Priority-based execution (early detection, late recovery)")
    print("\nFor async error handling, see 07_async_middleware.py")


if __name__ == "__main__":
    main()
