"""Manual middleware registration example.

Demonstrates using middleware WITHOUT the service pattern:
- Create MiddlewareManager directly (no DI)
- Register middleware instances manually
- Pass context as plain dict
- No svcs.Registry or Container needed

Use this pattern for simple applications or testing scenarios.
"""

from dataclasses import dataclass, field
from typing import Any, cast

from tdom_svcs.services.middleware import Context, MiddlewareManager


@dataclass
class LoggingMiddleware:
    """Simple logging middleware."""

    priority: int = -10
    logged: list = field(default_factory=list)

    def __call__(self, component, props, context):
        self.logged.append(component.__name__)
        return props


@dataclass
class TimestampMiddleware:
    """Add timestamp to props."""

    priority: int = 0

    def __call__(self, component, props, context):
        props["has_timestamp"] = True
        return props


@dataclass
class DebugMiddleware:
    """Debug middleware that checks context."""

    priority: int = 10
    debug_called: bool = False

    def __call__(self, component, props, context):
        if context.get("debug", False):
            self.debug_called = True
        return props


class Button:
    """Example component."""

    def __init__(self, title: str, **kwargs):
        self.title = title


def main() -> dict[str, Any]:
    """Execute middleware without DI container."""
    # Create manager directly
    manager = MiddlewareManager()

    # Register middleware instances
    logging_mw = LoggingMiddleware()
    debug_mw = DebugMiddleware()
    manager.register_middleware(logging_mw)
    manager.register_middleware(TimestampMiddleware())
    manager.register_middleware(debug_mw)

    # Create context as plain dict
    context: Context = cast(Context, {"debug": True, "user": "admin"})

    # Execute middleware chain
    props = {"title": "Click Me", "variant": "primary"}
    result = manager.execute(Button, props, context)

    # Verify execution
    assert result is not None
    assert result["has_timestamp"] is True
    assert "Button" in logging_mw.logged
    assert debug_mw.debug_called is True

    return result


if __name__ == "__main__":
    print(main())
