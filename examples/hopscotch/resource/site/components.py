"""A site that configures an app."""

from dataclasses import dataclass
from string.templatelib import Template

from svcs_hopscotch.injectors import injectable

from examples.hopscotch.resource.components import Greeting
from examples.hopscotch.resource.site.resources import FrenchCustomer


# docs: start french-greeting
@injectable(for_=Greeting, resource=FrenchCustomer)
@dataclass
class FrenchGreeting(Greeting):
    # Keep everything from the base Greeting

    def __call__(self) -> Template:
        return t"<h1>Bonjour {self.customer_name}!</h1>"
# docs: end french-greeting
