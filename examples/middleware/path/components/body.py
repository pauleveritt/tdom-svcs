"""Body component that uses the shared Greeting component."""

from dataclasses import dataclass

from svcs_di.injectors import injectable
from tdom import Node

from examples.common import Greeting
from tdom_svcs import html


@injectable
@dataclass
class Body:
    """Body component that renders a nested Greeting component."""

    def __call__(self, context=None) -> Node:
        """Render body element with greeting."""
        return html(t"<body><{Greeting} /></body>", context=context)
