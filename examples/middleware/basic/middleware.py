"""Middleware for the basic example.

Demonstrates:
- Chain execution with multiple middleware
- Priority ordering (lower numbers run first)
- Halting execution by returning None
- Prop transformation

All middleware use the @middleware decorator for automatic discovery by scan().
"""

from dataclasses import dataclass, field

from tdom_svcs import middleware
from tdom_svcs.types import Component, Context, Props, PropsResult


# Define middleware with decorators or imperatively
@middleware
@dataclass
class LoggingMiddleware:
    """Middleware that logs component processing.

    Priority -10 ensures this runs first in the chain.
    """

    priority: int = -10
    logged: list[str] = field(default_factory=list)

    def __call__(
        self, component: Component, props: Props, context: Context
    ) -> PropsResult:
        component_name = getattr(component, "__name__", type(component).__name__)
        self.logged.append(component_name)
        return props


@middleware
@dataclass
class ValidationMiddleware:
    """Middleware that validates props.

    Returns None to halt the middleware chain if validation fails.
    Priority 0 runs after logging but before transformation.
    """

    priority: int = 0

    def __call__(
        self, component: Component, props: Props, context: Context
    ) -> PropsResult:
        if "title" not in props:
            return None  # Halt execution
        return props


@middleware
@dataclass
class TransformationMiddleware:
    """Middleware that transforms props.

    Priority 10 ensures this runs last, after validation passes.
    """

    priority: int = 10

    def __call__(
        self, component: Component, props: Props, context: Context
    ) -> PropsResult:
        props["transformed"] = True
        return props
