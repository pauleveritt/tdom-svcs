"""Services for tdom-svcs integration."""

from .middleware import (
    Context,
    Middleware,
    component,
    register_component,
)

__all__ = [
    # Middleware (per-component)
    "Context",
    "Middleware",
    "component",
    "register_component",
]
