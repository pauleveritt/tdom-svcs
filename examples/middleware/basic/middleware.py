"""Middleware for the basic example.

Demonstrates:
- Chain execution with multiple middleware
- Priority ordering (lower numbers run first)
- Halting execution by returning None
- Prop transformation
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class LoggingMiddleware:
    """Middleware that logs component processing.

    Priority -10 ensures this runs first in the chain.
    """

    priority: int = -10
    logged: list[str] = field(default_factory=list)

    def __call__(
        self, component: type, props: dict[str, Any], context: Any
    ) -> dict[str, Any]:
        component_name = (
            component.__name__ if hasattr(component, "__name__") else str(component)
        )
        self.logged.append(component_name)
        return props


@dataclass
class ValidationMiddleware:
    """Middleware that validates props.

    Returns None to halt the middleware chain if validation fails.
    Priority 0 runs after logging but before transformation.
    """

    priority: int = 0

    def __call__(
        self, component: type, props: dict[str, Any], context: Any
    ) -> dict[str, Any] | None:
        if "title" not in props:
            return None  # Halt execution
        return props


@dataclass
class TransformationMiddleware:
    """Middleware that transforms props.

    Priority 10 ensures this runs last, after validation passes.
    """

    priority: int = 10

    def __call__(
        self, component: type, props: dict[str, Any], context: Any
    ) -> dict[str, Any]:
        props["transformed"] = True
        return props
