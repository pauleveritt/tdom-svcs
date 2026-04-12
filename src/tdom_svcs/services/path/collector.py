"""PathCollector service for tracking components and assets during rendering."""

import inspect
import re
from dataclasses import dataclass, field
from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path, PurePosixPath

from selectolax.parser import HTMLParser
from svcs_hopscotch.injectors import injectable

from tdom_svcs.services.path.types import AssetReference, ComponentLocation

# Compile regex once at module load time for performance
# Matches external URLs, special schemes, and anchor-only links
_EXTERNAL_URL_PATTERN = re.compile(
    r"^(https?://|//|mailto:|tel:|data:|javascript:|#)", re.IGNORECASE
)


def _should_process_href(href: str) -> bool:
    """Return True if href is a local path (not external/special URL)."""
    if not href:
        return False
    return not _EXTERNAL_URL_PATTERN.match(href)


def _normalize_module_name(module_name: str) -> str:
    """Strip repeated final component (e.g., ``a.heading.heading`` -> ``a.heading``)."""
    parts = module_name.split(".")
    if len(parts) >= 2 and parts[-1] == parts[-2]:
        return ".".join(parts[:-1])
    return module_name


def _get_component_file_path(component: type) -> Path:
    """Get the file path for a component's source file."""
    try:
        source_file = inspect.getfile(component)
        return Path(source_file)
    except TypeError, OSError:
        # Fallback for built-in or dynamically created components
        return Path("<unknown>")


@injectable
@dataclass
class PathCollector:
    """Collects component locations and static asset references during rendering.

    Unlike tdom-path which transforms paths, PathCollector only collects
    information. This data can be used by build tools, dev servers, or
    other systems that need to know about component assets.
    """

    components: set[ComponentLocation] = field(default_factory=set)
    assets: set[AssetReference] = field(default_factory=set)

    def register_component(self, component: type) -> ComponentLocation:
        """Register a component and return its ComponentLocation."""
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
        """Register an asset reference and resolve its module path."""
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
        self, node: object, component_location: ComponentLocation
    ) -> None:
        """Parse rendered HTML and collect local asset references (link/script tags)."""
        if not isinstance(node, str):
            return

        parser = HTMLParser(node)
        for element in parser.css("link[href], script[src]"):
            match element.tag:
                case "link":
                    href = element.attributes.get("href")
                    if href is not None and _should_process_href(href):
                        self.register_asset(component_location, href)
                case "script":
                    src = element.attributes.get("src")
                    if src is not None and _should_process_href(src):
                        self.register_asset(component_location, src)

    def clear(self) -> None:
        """Clear all collected components and assets."""
        self.components.clear()
        self.assets.clear()
