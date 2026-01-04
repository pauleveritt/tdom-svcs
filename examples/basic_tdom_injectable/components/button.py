"""Interactive components."""

from dataclasses import dataclass

from examples.basic_tdom_injectable.services.counter import Counter
from svcs_di import Inject
from svcs_di.injectors.decorators import injectable
from tdom import Node

from tdom_svcs import html


@injectable
@dataclass
class Button:
    counter: Inject[Counter]
    label: str = "Click Me"

    def __call__(self) -> Node:
        """Render the button with database status in the title."""
        return html(t"<button title={self.counter.name}>{self.label}</button>")
