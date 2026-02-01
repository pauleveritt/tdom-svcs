"""Components shared across examples."""

from dataclasses import dataclass

from svcs_di import Inject
from tdom import Node

from examples.common.services import Users
from tdom_svcs import html


@dataclass
class SimpleComponent:
    """Simple component for middleware examples - no DI dependencies."""

    def __call__(self) -> Node:
        return html(t"<div>Simple Component</div>")


@dataclass
class Greeting:
    """Greeting component that displays welcome message for current user."""

    users: Inject[Users]

    def __call__(self) -> Node:
        current_user = self.users.get_current_user()
        return html(t"<h1>Hello {current_user['name']}!</h1>")
