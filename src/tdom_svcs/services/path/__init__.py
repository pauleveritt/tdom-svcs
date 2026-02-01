"""Path collection service for tracking components and assets."""

from .collector import PathCollector
from .middleware import PathMiddleware
from .types import AssetReference, ComponentLocation

__all__ = [
    "AssetReference",
    "ComponentLocation",
    "PathCollector",
    "PathMiddleware",
]
