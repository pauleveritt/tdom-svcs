from dataclasses import dataclass
from typing import Protocol


class Customer(Protocol):
    name: str


@dataclass
class DefaultCustomer:
    name: str
