"""Services for tdom-svcs integration."""

from tdom_svcs.services.path import (
    AssetReference,
    ComponentLocation,
    PathCollector,
    PathMiddleware,
)

__all__ = [
    # Path collection
    "AssetReference",
    "ComponentLocation",
    "PathCollector",
    "PathMiddleware",
]
