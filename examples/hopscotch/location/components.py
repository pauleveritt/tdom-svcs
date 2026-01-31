"""Components built into the base app."""

from dataclasses import dataclass, field

from svcs_di import Inject
from tdom import Node

from examples.common.services import Users
from tdom_svcs import html


# A component that injects the Users service
@dataclass
class Greeting:
    """Greeting component that displays welcome message for current user."""

    users: Inject[Users]
    user_name: str = field(init=False)

    def __post_init__(self) -> None:
        current_user = self.users.get_current_user()
        self.user_name = current_user["name"]

    def __call__(self) -> Node:
        return html(t"<h1>Hello {self.user_name}!</h1>")
