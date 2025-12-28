"""tdom-svcs: Dependency injection for tdom templates."""

from .processor import ComponentLookup, Config, html
from .services import ComponentNameRegistry, ComponentNameRegistryProtocol

__all__ = [
    "ComponentLookup",
    "Config",
    "html",
    "ComponentNameRegistry",
    "ComponentNameRegistryProtocol",
]
