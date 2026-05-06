"""Components shared across examples."""

from dataclasses import dataclass
from string.templatelib import Template

from svcs_di import Inject

from examples.common.services import Users


@dataclass
class SimpleComponent:
    """Simple component for middleware examples - no DI dependencies."""

    def __call__(self) -> Template:
        return t"<div>Simple Component</div>"


# docs: start greeting-component
@dataclass
class Greeting:
    """Greeting component that displays welcome message for current user."""

    users: Inject[Users]

    def __call__(self) -> Template:
        current_user = self.users.get_current_user()
        return t"<h1>Hello {current_user['name']}!</h1>"


# docs: end greeting-component
