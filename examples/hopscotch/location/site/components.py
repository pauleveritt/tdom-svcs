"""A site that configures an app with location-based overrides."""

from dataclasses import dataclass
from pathlib import PurePath

from svcs_di.injectors import injectable
from tdom import Node

from examples.hopscotch.location.components import Greeting
from tdom_svcs import html


@injectable(for_=Greeting, location=PurePath("/fr"))
@dataclass
class FrenchGreeting(Greeting):
    """French greeting used when location starts with /fr."""

    def __call__(self) -> Node:
        return html(t"<h1>Bonjour {self.user_name}!</h1>")
