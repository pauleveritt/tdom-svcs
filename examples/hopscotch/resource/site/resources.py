from dataclasses import dataclass

from examples.hopscotch.resource.resources import DefaultCustomer


@dataclass
class FrenchCustomer(DefaultCustomer):
    pass
