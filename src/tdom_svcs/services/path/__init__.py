"""Path collection service for tracking components and assets."""

from tdom_svcs.services.path.collector import PathCollector
from tdom_svcs.services.path.middleware import PathMiddleware
from tdom_svcs.services.path.types import AssetReference, ComponentLocation

__all__ = [
    "AssetReference",
    "ComponentLocation",
    "PathCollector",
    "PathMiddleware",
]
