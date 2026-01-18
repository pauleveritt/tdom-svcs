from dataclasses import dataclass

from svcs_di import HopscotchRegistry

from tdom_svcs import Component
from tdom_svcs.services.middleware import (
    Context,
    setup_container,
)


@dataclass
class GlobalLoggingMiddleware:
    """Global logging middleware that runs for all components."""

    priority: int = -10

    def __call__(
        self,
        component: Component,
        props: dict,
        context: Context,
    ) -> dict | None:
        return props


def svcs_setup(registry: HopscotchRegistry, context: Context) -> None:
    """Configure the service registry for this application."""
    setup_container(context, registry)
