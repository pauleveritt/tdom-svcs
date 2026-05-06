"""A site that configures an app with location-based overrides."""

from dataclasses import dataclass
from pathlib import PurePath
from string.templatelib import Template

from svcs_hopscotch.injectors import injectable

from examples.hopscotch.location.components import Greeting


# docs: start french-greeting
@injectable(for_=Greeting, location=PurePath("/fr"))
@dataclass
class FrenchGreeting(Greeting):
    """French greeting used when location starts with /fr."""

    def __call__(self) -> Template:
        return t"<h1>Bonjour {self.user_name}!</h1>"


# docs: end french-greeting
