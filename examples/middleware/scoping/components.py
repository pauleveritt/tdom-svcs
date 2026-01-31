"""Components for the scoping middleware example.

Re-exports common Greeting and adds Button/Card with per-component middleware.
"""

from dataclasses import dataclass, field
from typing import Any

from tdom import Node

# Re-export common components
from examples.common.components import Greeting
from tdom_svcs import html
from tdom_svcs.services.middleware import component

__all__ = ["Button", "ButtonSpecificMiddleware", "button_mw", "Card", "Greeting"]


@dataclass
class ButtonSpecificMiddleware:
    """Middleware that only applies to Button components.

    Adds a default variant if not provided.
    """

    priority: int = -5
    logged: list[str] = field(default_factory=list)

    def __call__(
        self, component_type: type, props: dict[str, Any], context: Any
    ) -> dict[str, Any]:
        component_name = (
            component_type.__name__
            if hasattr(component_type, "__name__")
            else str(component_type)
        )
        self.logged.append(f"button:{component_name}")
        if "variant" not in props:
            props["variant"] = "primary"
        return props


# Create instance for use in decorator
button_mw = ButtonSpecificMiddleware()


@component(middleware={"pre_resolution": [button_mw]})
@dataclass
class Button:
    """Button component with per-component middleware.

    The @component decorator registers ButtonSpecificMiddleware
    to run only when this component is processed.
    """

    title: str = ""
    variant: str = "default"

    def __call__(self) -> Node:
        return html(t'<button class="{self.variant}">{self.title}</button>')


@dataclass
class Card:
    """Card component without per-component middleware.

    Only global middleware applies to this component.
    """

    title: str
    content: str = ""

    def __call__(self) -> Node:
        return html(
            t"""
            <div class="card">
                <h2>{self.title}</h2>
                <p>{self.content}</p>
            </div>
            """
        )
