"""Components built into the base app."""

from dataclasses import dataclass, field

from svcs_di.injectors import Resource
from tdom import Node

from examples.hopscotch.resource.resources import DefaultCustomer
from tdom_svcs import html


# A component that injects registered Customer resource
@dataclass
class Greeting:
    """Greeting component that displays welcome message for current resource."""

    customer: Resource[DefaultCustomer]
    customer_name: str = field(init=False)

    def __post_init__(self) -> None:
        self.customer_name = self.customer.name

    def __call__(self) -> Node:
        return html(t"<h1>Hello {self.customer_name}!</h1>")
