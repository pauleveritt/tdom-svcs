"""A site that configures an app."""

from dataclasses import dataclass

from svcs_di.hopscotch_registry import HopscotchRegistry
from tdom import Node

from examples.hopscotch.override.app_common import Greeting
from tdom_svcs import html


@dataclass
class FrenchGreeting(Greeting):
    """A unique Greeting for this site."""

    def __call__(self) -> Node:
        # Subclass the structure and any `__post_init__`, just change template
        current_user = self.users.get_current_user()
        return html(t"<h1>Bonjour {current_user['name']}!</h1>")


def svcs_registry(registry: HopscotchRegistry) -> None:
    """Called automatically during scan() - registers FrenchGreeting."""
    registry.register_implementation(Greeting, FrenchGreeting)
