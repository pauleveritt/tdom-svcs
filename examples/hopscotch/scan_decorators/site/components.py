"""A site that configures an app."""

from dataclasses import dataclass
from string.templatelib import Template

from svcs_hopscotch.injectors import injectable

from examples.hopscotch.scan_decorators.components import Greeting


# docs: start decorated-override
@injectable(for_=Greeting)
@dataclass
class FrenchGreeting(Greeting):
    """A unique Greeting for this site."""

    def __call__(self) -> Template:
        # Subclass the structure and any `__post_init__`, just change template
        current_user = self.users.get_current_user()
        return t"<h1>Bonjour {current_user['name']}!</h1>"


# docs: end decorated-override
