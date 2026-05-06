"""A site that configures an app."""

from dataclasses import dataclass
from string.templatelib import Template

from svcs_hopscotch.hopscotch_registry import HopscotchRegistry

from examples.hopscotch.override.app_common import Greeting


# docs: start override-component
@dataclass
class FrenchGreeting(Greeting):
    """A unique Greeting for this site."""

    def __call__(self) -> Template:
        # Subclass the structure and any `__post_init__`, just change template
        current_user = self.users.get_current_user()
        return t"<h1>Bonjour {current_user['name']}!</h1>"


# docs: end override-component


# docs: start register-override
def svcs_registry(registry: HopscotchRegistry) -> None:
    """Called automatically during scan() - registers FrenchGreeting."""
    registry.register_implementation(Greeting, FrenchGreeting)


# docs: end register-override
