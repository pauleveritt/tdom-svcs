"""Type definitions for path collection service."""

from dataclasses import dataclass
from importlib.resources.abc import Traversable
from pathlib import Path, PurePosixPath


@dataclass(frozen=True)
class ComponentLocation:
    """Information about a component's source location.

    This dataclass stores metadata about where a component is defined,
    enabling asset path resolution relative to the component's module.

    Attributes:
        component_type: The component class or function type
        module_name: Fully qualified module name (e.g., "examples.middleware.path.components.head")
        file_path: Absolute path to the component's source file

    Examples:
        >>> from examples.middleware.path.components.head import Head
        >>> location = ComponentLocation(
        ...     component_type=Head,
        ...     module_name="examples.middleware.path.components.head",
        ...     file_path=Path("/path/to/head.py")
        ... )
    """

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
    """Reference to a collected asset with source and component information.

    This dataclass stores information about static assets (CSS, JS files)
    encountered during rendering, enabling build tools to process them.

    Attributes:
        source: Traversable instance for reading file contents via .read_bytes()
        component_location: The component that owns this asset
        relative_path: Original path as written in template (e.g., "./static/styles.css")
        module_path: Resolved path using module structure (e.g., "examples/middleware/path/components/head/static/styles.css")

    Examples:
        >>> from pathlib import PurePosixPath
        >>> ref = AssetReference(
        ...     source=traversable,
        ...     component_location=location,
        ...     relative_path="./static/styles.css",
        ...     module_path=PurePosixPath("examples/middleware/path/components/head/static/styles.css")
        ... )
    """

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
