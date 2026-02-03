"""A site that configures an app."""

from dataclasses import dataclass

from svcs_di.injectors import injectable
from tdom import Node

from examples.hopscotch.scan_decorators.components import Greeting
from tdom_svcs import html


@injectable(for_=Greeting)
@dataclass
class FrenchGreeting(Greeting):
    """A unique Greeting for this site."""

    def __call__(self) -> Node:
        # Subclass the structure and any `__post_init__`, just change template
        current_user = self.users.get_current_user()
        return html(t"<h1>Bonjour {current_user['name']}!</h1>")
