"""Error handling middleware.

Demonstrates:
- Catching and handling exceptions in middleware
- Fallback rendering on error
- Circuit breaker pattern for fail-fast behavior

All middleware use the @middleware decorator for automatic discovery by scan().
The @injectable decorator registers them as services for DI resolution.
"""

from dataclasses import dataclass, field
from typing import Any

from tdom_svcs import middleware
from tdom_svcs.types import Component, Context, Props, PropsResult


class ValidationError(Exception):
    """Raised when component props fail validation."""

    pass


# The circuit breaker middleware
@middleware
@dataclass
class CircuitBreakerMiddleware:
    """Middleware implementing circuit breaker pattern.

    After a threshold of failures, the circuit "opens" and all
    subsequent requests fail fast without processing.

    Priority -10 ensures this runs very early to fail fast.
    """

    priority: int = -10
    failure_threshold: int = 3
    failure_count: int = 0
    circuit_open: bool = False

    def __call__(
        self, component: Component, props: Props, context: Context
    ) -> PropsResult:
        if self.circuit_open:
            return None

        # Check for conditions that indicate failure
        if props.get("invalid"):
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold:
                self.circuit_open = True
                return None

        return props

    def reset(self) -> None:
        """Reset the circuit breaker (for testing or recovery)."""
        self.failure_count = 0
        self.circuit_open = False


@middleware
@dataclass
class FallbackMiddleware:
    """Middleware that provides fallback rendering for missing data.

    Runs early (-5 priority) to provide default values before other
    middleware process the props.
    """

    priority: int = -5
    defaults: dict[str, Any] = field(default_factory=dict)

    def __call__(
        self, component: Component, props: Props, context: Context
    ) -> PropsResult:
        # Apply defaults for any missing props
        for key, value in self.defaults.items():
            if key not in props:
                props[key] = value
        return props


@middleware
@dataclass
class ErrorHandlingMiddleware:
    """Middleware that wraps execution with error handling.

    Catches ValidationError and either returns fallback props or halts.
    Has high priority (100) so it runs late and can catch errors from
    earlier middleware.
    """

    priority: int = 100
    fallback_props: dict[str, Any] = field(default_factory=dict)
    errors_handled: list[str] = field(default_factory=list)

    def __call__(
        self, component: Component, props: Props, context: Context
    ) -> PropsResult:
        try:
            # Simulate validation that could fail
            if props.get("invalid"):
                component_name = getattr(
                    component, "__name__", type(component).__name__
                )
                raise ValidationError(f"Invalid prop in {component_name}")
            return props
        except ValidationError as e:
            self.errors_handled.append(str(e))
            if self.fallback_props:
                # Return fallback props merged with original
                return {**props, **self.fallback_props}
            return None
