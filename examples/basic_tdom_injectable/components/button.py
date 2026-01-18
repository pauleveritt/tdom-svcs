"""Interactive components."""

from dataclasses import dataclass

from tdom import Node

from tdom_svcs import html


@dataclass
class Button:
    """Simple button component."""

    label: str = "Click Me"

    def __call__(self) -> Node:
        """Render a simple button."""
        return html(t"<button>{self.label}</button>")
