"""tdom-svcs: Dependency injection for tdom templates."""

from tdom_svcs.processor import ComponentLookup, Config, html
from tdom_svcs.scanning import scan_components
from tdom_svcs.services import ComponentNameRegistry, ComponentNameRegistryProtocol
__all__ = [
    "ComponentLookup",
    "Config",
    "html",
    "ComponentNameRegistry",
    "ComponentNameRegistryProtocol",
    "scan_components",
]
