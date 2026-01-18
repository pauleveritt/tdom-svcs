from dataclasses import dataclass
from typing import Any

from tdom import Node
from tdom_svcs import html
from tdom_svcs.services.middleware import Context, component
from tdom_svcs.types import Component


@dataclass
class ButtonSpecificMiddleware:
    """Middleware specific to Button components."""

    priority: int = -5

    def __call__(
        self,
        component: Component,
        props: dict[str, Any],
        context: Context,
    ) -> dict[str, Any] | None:
        if "variant" not in props:
            props["variant"] = "primary"
        return props


@component(
    middleware={
        "pre_resolution": [
            ButtonSpecificMiddleware(),
        ]
    }
)
@dataclass
class Button:
    title: str = ""
    variant: str = "default"

    def __call__(self) -> Node:
        return html(t"<button class='{self.variant}'>{self.title}</button>")
