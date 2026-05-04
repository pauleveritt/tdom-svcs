"""Package scanning for tdom-svcs decorators.

This module provides scan() which wraps svcs_hopscotch's scan() and uses
injectable metadata to discover @middleware and @hookable decorated classes.

Example:
    from tdom_svcs import scan

    registry = HopscotchRegistry()
    scan(registry, my_services, my_middleware, my_components)
"""

from types import ModuleType
from typing import Any

from svcs_hopscotch.injectors.scanning import scan as svcs_scan


def scan(
    registry: Any,
    *packages: str | ModuleType | None,
    locals_dict: dict[str, Any] | None = None,
) -> Any:
    """Scan packages for services, middleware, and hookable targets.

    Wraps svcs_hopscotch's scan() which discovers all @injectable subclasses
    (including @middleware and @hookable) in a single pass.

    Returns the registry instance for method chaining.

    Example:
        >>> from tdom_svcs import scan
        >>> registry = HopscotchRegistry()
        >>> scan(registry, "myapp.services", "myapp.middleware", "myapp.components")
        >>> # For testing:
        >>> scan(registry, locals_dict=locals())
    """
    if locals_dict is not None:
        svcs_scan(registry, locals_dict=locals_dict)
    else:
        svcs_scan(registry, *packages)

    return registry
