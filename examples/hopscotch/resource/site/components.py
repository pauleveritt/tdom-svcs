"""A site that configures an app."""

from dataclasses import dataclass

from svcs_hopscotch.injectors import injectable
from markupsafe import Markup

from examples.hopscotch.resource.components import Greeting
from examples.hopscotch.resource.site.resources import FrenchCustomer
from tdom_svcs import html


@injectable(for_=Greeting, resource=FrenchCustomer)
@dataclass
class FrenchGreeting(Greeting):
    # Keep everything from the base Greeting

    def __call__(self) -> str | Markup:
        return html(t"<h1>Bonjour {self.customer_name}!</h1>")
