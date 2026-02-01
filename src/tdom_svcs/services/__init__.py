"""Services for tdom-svcs integration."""

from .middleware import (
    Context,
    ContextNotSetupError,
    Middleware,
    MiddlewareConfigurationError,
    MiddlewareError,
    MiddlewareExecutionError,
    component,
    get_component_middleware,
    register_component,
)

__all__ = [
    # Middleware (per-component)
    "Context",
    "ContextNotSetupError",
    "Middleware",
    "MiddlewareConfigurationError",
    "MiddlewareError",
    "MiddlewareExecutionError",
    "component",
    "get_component_middleware",
    "register_component",
]
