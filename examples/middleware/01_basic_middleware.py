"""Basic middleware usage example.

Demonstrates the recommended pattern for using middleware as a service:
- Setup context and register MiddlewareManager as a service
- Get MiddlewareManager via dependency injection
- Register middleware instances
- Execute middleware chain
"""

from dataclasses import dataclass
from typing import Any, cast

from svcs_di import HopscotchContainer, HopscotchRegistry

from tdom_svcs.services.middleware import Context, MiddlewareManager, setup_container


@dataclass
class LoggingMiddleware:
    """Middleware that logs component processing."""

    priority: int = -10
    logged: list = None  # For testing - captures what was logged

    def __post_init__(self):
        self.logged = []

    def __call__(self, component, props, context):
        self.logged.append(component.__name__)
        return props


@dataclass
class ValidationMiddleware:
    """Middleware that validates props."""

    priority: int = 0

    def __call__(self, component, props, context):
        if "title" not in props:
            return None  # Halt execution
        return props


@dataclass
class TransformationMiddleware:
    """Middleware that transforms props."""

    priority: int = 10

    def __call__(self, component, props, context):
        props["transformed"] = True
        return props


class Button:
    """Example component."""

    def __init__(self, title: str, **kwargs):
        self.title = title


def main() -> dict[str, Any]:
    """Execute middleware chain and return final props."""
    registry = HopscotchRegistry()
    context: Context = cast(Context, {"config": {"debug": True}})

    # Setup container (registers MiddlewareManager as service)
    setup_container(context, registry)

    with HopscotchContainer(registry) as container:
        manager = container.get(MiddlewareManager)

        # Register middleware
        logging_mw = LoggingMiddleware()
        manager.register_middleware(logging_mw)
        manager.register_middleware(ValidationMiddleware())
        manager.register_middleware(TransformationMiddleware())

        # Execute with valid props
        props = {"title": "Click Me", "variant": "primary"}
        result = manager.execute(Button, props, context)

        # Verify successful execution
        assert result is not None
        assert result["title"] == "Click Me"
        assert result["transformed"] is True
        assert "Button" in logging_mw.logged

        # Execute with invalid props (missing title)
        invalid_props = {"variant": "secondary"}
        halted_result = manager.execute(Button, invalid_props, context)

        # Verify validation halted execution
        assert halted_result is None

        return result


if __name__ == "__main__":
    print(main())
