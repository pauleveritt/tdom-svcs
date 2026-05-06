from dataclasses import dataclass

from examples.hopscotch.resource.resources import DefaultCustomer


# docs: start french-resource
@dataclass
class FrenchCustomer(DefaultCustomer):
    pass


# docs: end french-resource
