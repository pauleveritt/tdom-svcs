"""Package scanning for tdom-svcs decorators.

This module provides scan() which wraps svcs_di's scan() and additionally
discovers @middleware and @component decorated classes, registering them
with the registry.

Example:
    from tdom_svcs import scan

    registry = HopscotchRegistry()
    scan(registry, my_services, my_middleware, my_components)
"""

import importlib
import inspect
import logging
from types import ModuleType
from typing import Any

from svcs_di.injectors.scanning import scan as svcs_scan

from tdom_svcs.middleware import (
    MIDDLEWARE_METADATA_ATTR,
    register_middleware,
)
from tdom_svcs.services.middleware.decorators import (
    COMPONENT_MIDDLEWARE_ATTR,
    register_component_middleware,
)

log = logging.getLogger("tdom_svcs")


def _resolve_module(package: str | ModuleType | None) -> ModuleType | None:
    """Resolve a package reference to a module."""
    if package is None:
        return None
    if isinstance(package, ModuleType):
        return package
    try:
        return importlib.import_module(package)
    except ImportError as e:
        log.warning(f"Failed to import package '{package}': {e}")
        return None


def _get_all_modules(packages: tuple[str | ModuleType | None, ...]) -> list[ModuleType]:
    """Get all modules from package references, including submodules."""
    import pkgutil

    modules: list[ModuleType] = []

    for pkg in packages:
        module = _resolve_module(pkg)
        if module is None:
            continue

        modules.append(module)

        # Walk submodules if it's a package
        module_path = getattr(module, "__path__", None)
        if module_path is not None:
            for _, modname, _ in pkgutil.walk_packages(
                path=module_path,
                prefix=module.__name__ + ".",
                onerror=lambda name: None,
            ):
                try:
                    submodule = importlib.import_module(modname)
                    modules.append(submodule)
                except ImportError as e:
                    log.warning(f"Failed to import submodule '{modname}': {e}")

    return modules


def _scan_for_middleware(registry: Any, modules: list[ModuleType]) -> None:
    """Find @middleware decorated classes and register them."""
    for module in modules:
        for attr_name in dir(module):
            try:
                obj = getattr(module, attr_name)
                if inspect.isclass(obj) and hasattr(obj, MIDDLEWARE_METADATA_ATTR):
                    register_middleware(registry, obj)
                    log.debug(f"Registered middleware: {obj.__name__}")
            except (AttributeError, ImportError):
                continue


def _scan_for_component_middleware(registry: Any, modules: list[ModuleType]) -> None:
    """Find @component decorated classes and register their middleware."""
    for module in modules:
        for attr_name in dir(module):
            try:
                obj = getattr(module, attr_name)
                if (inspect.isclass(obj) or inspect.isfunction(obj)) and hasattr(
                    obj, COMPONENT_MIDDLEWARE_ATTR
                ):
                    middleware_config = getattr(obj, COMPONENT_MIDDLEWARE_ATTR)
                    register_component_middleware(registry, obj, middleware_config)
                    log.debug(f"Registered component middleware: {getattr(obj, '__name__', obj)}")
            except (AttributeError, ImportError):
                continue


def _scan_locals_dict(registry: Any, locals_dict: dict[str, Any]) -> None:
    """Scan a locals dictionary for decorated classes."""
    for obj in locals_dict.values():
        if inspect.isclass(obj):
            if hasattr(obj, MIDDLEWARE_METADATA_ATTR):
                register_middleware(registry, obj)
                log.debug(f"Registered middleware: {obj.__name__}")
            if hasattr(obj, COMPONENT_MIDDLEWARE_ATTR):
                middleware_config = getattr(obj, COMPONENT_MIDDLEWARE_ATTR)
                register_component_middleware(registry, obj, middleware_config)
                log.debug(f"Registered component middleware: {obj.__name__}")
        elif inspect.isfunction(obj):
            if hasattr(obj, COMPONENT_MIDDLEWARE_ATTR):
                middleware_config = getattr(obj, COMPONENT_MIDDLEWARE_ATTR)
                register_component_middleware(registry, obj, middleware_config)
                log.debug(f"Registered component middleware: {obj.__name__}")


def scan(
    registry: Any,
    *packages: str | ModuleType | None,
    locals_dict: dict[str, Any] | None = None,
) -> Any:
    """Scan packages for services, middleware, and component middleware.

    This function wraps svcs_di's scan() and additionally discovers:
    - @middleware decorated classes (global middleware)
    - @component decorated classes (per-component middleware)

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
    # Handle locals_dict scanning for testing
    if locals_dict is not None:
        svcs_scan(registry, locals_dict=locals_dict)
        _scan_locals_dict(registry, locals_dict)
        return registry

    # First, run svcs_di's scan for @injectable services
    svcs_scan(registry, *packages)

    # Get all modules to scan for tdom decorators
    modules = _get_all_modules(packages)

    # Scan for @middleware decorated classes
    _scan_for_middleware(registry, modules)

    # Scan for @component decorated classes
    _scan_for_component_middleware(registry, modules)

    return registry
