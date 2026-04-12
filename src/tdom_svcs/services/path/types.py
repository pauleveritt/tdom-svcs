"""Type definitions for path collection service."""

from dataclasses import dataclass
from importlib.resources.abc import Traversable
from pathlib import Path, PurePosixPath


@dataclass(frozen=True)
class ComponentLocation:
    """Where a component is defined -- enables asset path resolution relative to its module."""

    component_type: type
    module_name: str
    file_path: Path

    def __hash__(self) -> int:
        """Hash based on component type for set membership."""
        return hash(self.component_type)

    def __eq__(self, other: object) -> bool:
        """Equality based on component type."""
        if not isinstance(other, ComponentLocation):
            return NotImplemented
        return self.component_type == other.component_type


@dataclass(frozen=True)
class AssetReference:
    """A static asset (CSS, JS) encountered during rendering, with resolved paths."""

    source: Traversable
    component_location: ComponentLocation
    relative_path: str
    module_path: PurePosixPath

    def __hash__(self) -> int:
        """Hash based on module_path for set deduplication."""
        return hash(self.module_path)

    def __eq__(self, other: object) -> bool:
        """Equality based on module_path."""
        if not isinstance(other, AssetReference):
            return NotImplemented
        return self.module_path == other.module_path
