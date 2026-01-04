"""Services for tdom-svcs integration."""

from .middleware import (
    Context,
    ContextNotSetupError,
    Middleware,
    MiddlewareConfigurationError,
    MiddlewareError,
    MiddlewareExecutionError,
    MiddlewareManager,
    component,
    get_component_middleware,
    register_component,
    setup_container,
)

__all__ = [
    # Middleware
    "Context",
    "ContextNotSetupError",
    "Middleware",
    "MiddlewareConfigurationError",
    "MiddlewareError",
    "MiddlewareExecutionError",
    "MiddlewareManager",
    "component",
    "get_component_middleware",
    "register_component",
    "setup_container",
]
