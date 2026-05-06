from dataclasses import dataclass
from typing import Protocol


# docs: start default-resource
class Customer(Protocol):
    name: str


@dataclass
class DefaultCustomer:
    name: str


# docs: end default-resource
