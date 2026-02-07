"""Package scanning for tdom-svcs decorators.

This module provides scan() which wraps svcs_di's scan() and uses injectable
categories to discover @middleware and @component decorated classes.

Example:
    from tdom_svcs import scan

    registry = HopscotchRegistry()
    scan(registry, my_services, my_middleware, my_components)
"""

import logging
from types import ModuleType
from typing import Any

from svcs_di.injectors.scanning import scan as svcs_scan

from tdom_svcs.services.middleware.decorators import COMPONENT_MIDDLEWARE_ATTR

log = logging.getLogger("tdom_svcs")


def _register_component_middlewares(registry: Any) -> None:
    """Register MiddlewareMap configs for @component-decorated types.

    This post-scan step retrieves all component types from the registry's
    "component" category and ensures their middleware configurations are set.
    """
    for comp_type in registry.get_by_category("component"):
        mw_config = getattr(comp_type, COMPONENT_MIDDLEWARE_ATTR, {})
        if mw_config:
            # Middleware config is already set by @component decorator
            # This just logs for debugging
            log.debug(
                f"Found component middleware: {getattr(comp_type, '__name__', comp_type)}"
            )


def scan(
    registry: Any,
    *packages: str | ModuleType | None,
    locals_dict: dict[str, Any] | None = None,
) -> Any:
    """Scan packages for services, middleware, and component middleware.

    This function wraps svcs_di's scan() which discovers all @injectable
    subclasses (including @middleware and @component) in a single pass.
    After scanning, component middleware configurations are registered.

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

    # Component middleware maps need post-scan registration
    _register_component_middlewares(registry)

    return registry
