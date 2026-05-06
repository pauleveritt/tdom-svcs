"""Tiny components for tdom-svcs domain stories."""

from dataclasses import dataclass

from svcs_di import Inject


@dataclass
class GreetingService:
    """Small service used by the domain story component."""

    name: str


@dataclass
class InjectedGreeting:
    """Component with an injected field that can be overridden by template attrs."""

    greeting: Inject[GreetingService]

    def __call__(self) -> str:
        return f"<p>Hello {self.greeting.name}</p>"
