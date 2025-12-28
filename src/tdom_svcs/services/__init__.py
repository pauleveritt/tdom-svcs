"""Services for tdom-svcs integration."""

from .component_lookup import (
    ComponentLookup,
    ComponentLookupProtocol,
    ComponentNotFoundError,
    InjectorNotFoundError,
    RegistryNotSetupError,
)
from .component_registry import ComponentNameRegistry, ComponentNameRegistryProtocol

__all__ = [
    "ComponentLookup",
    "ComponentLookupProtocol",
    "ComponentNameRegistry",
    "ComponentNameRegistryProtocol",
    "ComponentNotFoundError",
    "InjectorNotFoundError",
    "RegistryNotSetupError",
]
