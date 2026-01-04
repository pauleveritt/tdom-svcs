from dataclasses import dataclass
from svcs import Registry
from tdom_svcs.services.middleware import (
    Context,
    setup_container,
)
from tdom_svcs import Component


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
        print(f"  [GLOBAL-LOG] Processing {component}")
        return props


def svcs_setup(registry: Registry, context: dict):
    """Configure the service registry for this application."""
    setup_container(context, registry)
