"""Package scanning for tdom-svcs decorators.

This module provides scan() which wraps svcs_di's scan() and uses injectable
categories to discover @middleware and @component decorated classes.

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
    """Scan packages for services, middleware, and component middleware.

    This function wraps svcs_di's scan() which discovers all @injectable
    subclasses (including @middleware and @component) in a single pass.

    Args:
        registry: HopscotchRegistry to register with.
        *packages: Package/module references to scan.
        locals_dict: Dictionary of local variables to scan (useful for testing).

    Returns:
        The registry instance for method chaining.

    Example:
        >>> from tdom_svcs import scan
        >>> registry = HopscotchRegistry()
        >>> scan(registry, "myapp.services", "myapp.middleware", "myapp.components")
        >>> # For testing:
        >>> scan(registry, locals_dict=locals())
    """
    # svcs_scan discovers all @injectable subclasses (services, middleware, components)
    if locals_dict is not None:
        svcs_scan(registry, locals_dict=locals_dict)
    else:
        svcs_scan(registry, *packages)

    return registry
