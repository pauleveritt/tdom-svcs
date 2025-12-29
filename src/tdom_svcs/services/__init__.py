"""Services for tdom-svcs integration."""

from .component_lookup import (
    ComponentLookup,
    ComponentLookupProtocol,
    ComponentNotFoundError,
    InjectorNotFoundError,
    RegistryNotSetupError,
)
from .component_registry import ComponentNameRegistry, ComponentNameRegistryProtocol
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
    "ComponentLookup",
    "ComponentLookupProtocol",
    "ComponentNameRegistry",
    "ComponentNameRegistryProtocol",
    "ComponentNotFoundError",
    "InjectorNotFoundError",
    "RegistryNotSetupError",
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
