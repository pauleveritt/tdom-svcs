"""Components for the scoping middleware example.

Demonstrates per-component middleware via the @component decorator.
"""

from dataclasses import dataclass, field

from svcs_di.injectors import injectable
from tdom import Node

from tdom_svcs import component, html
from tdom_svcs.types import Component, Context, Props, PropsResult


@injectable
@dataclass
class ButtonSpecificMiddleware:
    """Middleware that only applies to Button components.

    Adds a default variant if not provided.
    """

    priority: int = -5
    logged: list[str] = field(default_factory=list)

    def __call__(
        self, component: Component, props: Props, context: Context
    ) -> PropsResult:
        component_name = getattr(component, "__name__", type(component).__name__)
        self.logged.append(f"button:{component_name}")
        if "variant" not in props:
            props["variant"] = "primary"
        return props


# Button component with per-component middleware
@component(middleware={"pre_resolution": [ButtonSpecificMiddleware]})
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

    title: str = ""
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
