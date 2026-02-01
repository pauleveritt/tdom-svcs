"""PathCollector service for tracking components and assets during rendering."""

import inspect
import re
from dataclasses import dataclass, field
from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path, PurePosixPath
from typing import Any

from tdom import Element, Fragment, Node

from .types import AssetReference, ComponentLocation

# Compile regex once at module load time for performance
# Matches external URLs, special schemes, and anchor-only links
_EXTERNAL_URL_PATTERN = re.compile(
    r"^(https?://|//|mailto:|tel:|data:|javascript:|#)", re.IGNORECASE
)


def _should_process_href(href: str | None) -> bool:
    """Check if href should be processed (skip external/special URLs).

    Args:
        href: The href or src attribute value to check

    Returns:
        True if the href should be processed, False otherwise
    """
    if not isinstance(href, str) or not href:
        return False
    return not _EXTERNAL_URL_PATTERN.match(href)


def _normalize_module_name(module_name: str) -> str:
    """Normalize module name by stripping repeated final component.

    If a module ends with a repeated component (e.g., mysite.components.heading.heading),
    strip the last component to get the package path (mysite.components.heading).

    Args:
        module_name: The module name to normalize

    Returns:
        Normalized module name with repeated component removed if present
    """
    parts = module_name.split(".")
    if len(parts) >= 2 and parts[-1] == parts[-2]:
        return ".".join(parts[:-1])
    return module_name


def _get_component_file_path(component: type) -> Path:
    """Get the file path for a component.

    Args:
        component: The component class or function

    Returns:
        Path to the component's source file
    """
    try:
        source_file = inspect.getfile(component)
        return Path(source_file)
    except (TypeError, OSError):
        # Fallback for built-in or dynamically created components
        return Path("<unknown>")


@dataclass
class PathCollector:
    """Service for collecting component locations and asset references.

    PathCollector tracks components and their static assets during rendering.
    It provides methods to register components, detect assets from Node trees,
    and query the collected data.

    Unlike tdom-path which transforms paths, PathCollector only collects
    information. This data can be used by build tools, dev servers, or
    other systems that need to know about component assets.

    Attributes:
        components: Set of ComponentLocation instances for registered components
        assets: Set of AssetReference instances for detected assets

    Examples:
        >>> collector = PathCollector()
        >>> location = collector.register_component(MyComponent)
        >>> collector.collect_from_node(rendered_node, location)
        >>> print(f"Found {len(collector.assets)} assets")
    """

    components: set[ComponentLocation] = field(default_factory=set)
    assets: set[AssetReference] = field(default_factory=set)

    def register_component(self, component: type) -> ComponentLocation:
        """Register a component and return its location information.

        Creates a ComponentLocation for the given component type,
        stores it in the components set, and returns it.

        Args:
            component: The component class or callable to register

        Returns:
            ComponentLocation with component metadata

        Examples:
            >>> collector = PathCollector()
            >>> location = collector.register_component(MyComponent)
            >>> location.module_name
            'myapp.components.my_component'
        """
        module_name = getattr(component, "__module__", "unknown")
        module_name = _normalize_module_name(module_name)
        file_path = _get_component_file_path(component)

        location = ComponentLocation(
            component_type=component,
            module_name=module_name,
            file_path=file_path,
        )

        self.components.add(location)
        return location

    def register_asset(
        self, component_location: ComponentLocation, relative_path: str
    ) -> AssetReference:
        """Register an asset reference for a component.

        Creates an AssetReference linking the asset to its owning component,
        resolves the module path, and stores it in the assets set.

        Args:
            component_location: The component that owns this asset
            relative_path: Original path as in template (e.g., "./static/styles.css")

        Returns:
            AssetReference with resolved paths

        Examples:
            >>> collector = PathCollector()
            >>> location = collector.register_component(Head)
            >>> ref = collector.register_asset(location, "./static/styles.css")
            >>> str(ref.module_path)
            'examples/middleware/path/components/head/static/styles.css'
        """
        # Calculate module path from module name + relative path
        module_web_path = component_location.module_name.replace(".", "/")
        clean_relative = relative_path.lstrip("./")
        module_path = PurePosixPath(module_web_path) / clean_relative

        # Create Traversable for asset access
        try:
            module_root = files(component_location.module_name)
            source: Traversable = module_root
            for part in clean_relative.split("/"):
                if part:
                    source = source / part
        except Exception:
            # If we can't resolve the asset, create a placeholder
            # This allows collection to continue even with missing assets
            source = files(component_location.module_name)

        asset_ref = AssetReference(
            source=source,
            component_location=component_location,
            relative_path=relative_path,
            module_path=module_path,
        )

        self.assets.add(asset_ref)
        return asset_ref

    def collect_from_node(
        self, node: Node, component_location: ComponentLocation
    ) -> None:
        """Walk a Node tree and collect asset references.

        Recursively traverses the Node tree looking for <link href="...">
        and <script src="..."> elements. For each found asset, creates
        an AssetReference linking it to the owning component.

        Skips external URLs (http://, https://, //), special schemes
        (mailto:, tel:, data:, javascript:), and anchor-only links (#).

        Args:
            node: Root node of the tree to scan
            component_location: The component that rendered this node

        Examples:
            >>> collector = PathCollector()
            >>> location = collector.register_component(Head)
            >>> tree = html(t'<link rel="stylesheet" href="./static/styles.css">')
            >>> collector.collect_from_node(tree, location)
            >>> len(collector.assets)
            1
        """
        self._walk_and_collect(node, component_location)

    def _walk_and_collect(
        self, node: Node, component_location: ComponentLocation
    ) -> None:
        """Internal recursive walker for asset collection."""
        # Check for asset elements
        self._check_for_asset(node, component_location)

        # Recurse into children
        match node:
            case Element(children=children) if children:
                for child in children:
                    self._walk_and_collect(child, component_location)
            case Fragment(children=children) if children:
                for child in children:
                    self._walk_and_collect(child, component_location)

    def _check_for_asset(
        self, node: Any, component_location: ComponentLocation
    ) -> None:
        """Check if a node is an asset element and register it."""
        match node:
            case Element(tag="link", attrs=attrs):
                href = attrs.get("href")
                if _should_process_href(href):
                    self.register_asset(component_location, href)

            case Element(tag="script", attrs=attrs):
                src = attrs.get("src")
                if _should_process_href(src):
                    self.register_asset(component_location, src)

    def clear(self) -> None:
        """Clear all collected components and assets.

        Useful for resetting state between renders or tests.

        Examples:
            >>> collector = PathCollector()
            >>> collector.register_component(MyComponent)
            >>> collector.clear()
            >>> len(collector.components)
            0
        """
        self.components.clear()
        self.assets.clear()
