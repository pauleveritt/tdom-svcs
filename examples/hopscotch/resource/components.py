"""Components built into the base app."""

from dataclasses import dataclass, field
from string.templatelib import Template

from svcs_hopscotch.injectors import Resource

from examples.hopscotch.resource.resources import DefaultCustomer


# A component that injects registered Customer resource
# docs: start resource-greeting
@dataclass
class Greeting:
    """Greeting component that displays welcome message for current resource."""

    customer: Resource[DefaultCustomer]
    customer_name: str = field(init=False)

    def __post_init__(self) -> None:
        self.customer_name = self.customer.name

    def __call__(self) -> Template:
        return t"<h1>Hello {self.customer_name}!</h1>"


# docs: end resource-greeting
