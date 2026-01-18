"""Global and per-component middleware example.

Demonstrates the comprehensive middleware system:
- Global middleware via MiddlewareManager (applies to all components)
- Per-component middleware via @component decorator
- Execution order: global first, then per-component
- Priority ordering within each group
"""

from dataclasses import dataclass, field
from typing import Any, cast

from svcs_di import HopscotchContainer, HopscotchRegistry

from tdom_svcs.services.middleware import (
    Context,
    MiddlewareManager,
    component,
    get_component_middleware,
    setup_container,
)


@dataclass
class GlobalLoggingMiddleware:
    """Global logging middleware that runs for all components."""

    priority: int = -10
    logged: list = field(default_factory=list)

    def __call__(self, component, props, context):
        self.logged.append(f"global:{component.__name__}")
        return props


@dataclass
class GlobalValidationMiddleware:
    """Global validation middleware."""

    priority: int = 0

    def __call__(self, component, props, context):
        if not props:
            return None
        return props


@dataclass
class ButtonSpecificMiddleware:
    """Middleware specific to Button components."""

    priority: int = -5
    logged: list = field(default_factory=list)

    def __call__(self, component, props, context):
        self.logged.append(f"button:{component.__name__}")
        if "variant" not in props:
            props["variant"] = "primary"
        return props


# Button with per-component middleware
button_mw = ButtonSpecificMiddleware()


@component(middleware={"pre_resolution": [button_mw]})
@dataclass
class Button:
    """Button component with per-component middleware."""

    title: str = ""
    variant: str = "default"


@dataclass
class Card:
    """Card component without per-component middleware."""

    title: str
    content: str = ""


def main() -> dict[str, Any]:
    """Execute global and per-component middleware."""
    registry = HopscotchRegistry()
    context: Context = cast(Context, {"config": {"debug": True}})

    setup_container(context, registry)

    with HopscotchContainer(registry) as container:
        manager = container.get(MiddlewareManager)

        # Register global middleware
        global_logging = GlobalLoggingMiddleware()
        manager.register_middleware(global_logging)
        manager.register_middleware(GlobalValidationMiddleware())

        # Execute for Button (has per-component middleware)
        button_props = {"title": "Click Me"}
        result = manager.execute(Button, button_props, context)
        assert result is not None

        # Execute per-component middleware
        component_mw = get_component_middleware(Button)
        for mw in component_mw.get("pre_resolution", []):
            mw_result = mw(Button, result, context)
            # Per-component middleware in examples is always sync
            if isinstance(mw_result, dict):
                result = mw_result

        # Verify global middleware ran
        assert "global:Button" in global_logging.logged

        # Verify per-component middleware ran and added default variant
        assert "button:Button" in button_mw.logged
        assert result is not None and result["variant"] == "primary"

        # Execute for Card (no per-component middleware)
        card_props = {"title": "Welcome", "content": "Hello"}
        card_result = manager.execute(Card, card_props, context)
        assert card_result is not None
        assert "global:Card" in global_logging.logged

        return {
            "button_result": result,
            "card_result": card_result,
            "global_logged": global_logging.logged,
            "button_logged": button_mw.logged,
        }


if __name__ == "__main__":
    print(main())
