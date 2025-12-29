"""
Component scanning infrastructure for tdom-svcs.

This module provides the scan_components() function that discovers @injectable
decorated classes in packages and registers them in both ComponentNameRegistry
(for string name lookup) and svcs.Registry (for type-based dependency injection).

The scanning leverages svcs-di's scanning infrastructure to handle package
traversal, module discovery, and error handling.

Overview
--------

The component discovery workflow consists of three main parts:

1. **Decoration**: Mark component classes with @injectable from svcs-di
2. **Scanning**: Call scan_components() at application startup
3. **Resolution**: Components are resolved by string name via ComponentLookup

Component Discovery Process
----------------------------

When you decorate a class with @injectable and scan it:

1. The @injectable decorator stores metadata on the class
2. scan_components() discovers decorated classes in specified packages
3. Components are registered in ComponentNameRegistry (by class.__name__)
4. Components are registered in svcs.Registry (by type, for DI)
5. ComponentLookup can resolve components by string name
6. Injector constructs instances with Inject[] dependencies resolved

Basic Usage
-----------

::

    import svcs
    from svcs_di.injectors.decorators import injectable
    from svcs_di import Inject
    from tdom_svcs import ComponentNameRegistry, scan_components

    # Step 1: Decorate component classes
    @injectable
    @dataclass
    class Button:
        label: str = "Click me"

        def __call__(self) -> str:
            return f"<button>{self.label}</button>"

    # Step 2: Setup and scan at application startup
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()

    scan_components(
        registry,
        component_registry,
        "myapp.components",  # Scan your component packages
        "myapp.widgets",
    )

    container = svcs.Container(registry)
    # Now components are discoverable by string name "Button"

Decorator Usage
---------------

Import @injectable from svcs-di::

    from svcs_di.injectors.decorators import injectable

The decorator supports several usage patterns:

**Bare decorator (most common)**::

    @injectable
    @dataclass
    class Button:
        label: str = "Click me"

**Resource-based registration**::

    @injectable(resource=CustomerContext)
    @dataclass
    class CustomerDashboard:
        user: Inject[UserService]

**Location-based registration**::

    from pathlib import PurePath

    @injectable(location=PurePath("/admin"))
    @dataclass
    class AdminPanel:
        auth: Inject[AuthService]

**Direct application (without decorator syntax)**::

    @dataclass
    class Card:
        title: str
        content: str

    # Apply decorator programmatically (no reassignment needed)
    injectable(Card)

    # Or with parameters (using decorator pattern)
    Card = injectable(resource=CustomerContext)(Card)

Inject[] Parameter Usage
------------------------

Use Inject[] from svcs-di to mark dependencies for injection::

    from svcs_di import Inject

    @injectable
    @dataclass
    class UserProfile:
        user_id: int = 1  # Regular parameter with default
        db: Inject[DatabaseService] = None  # Injected from container

        def __call__(self) -> str:
            user = self.db.get_user(self.user_id)
            return f"<div>User: {user['name']}</div>"

**Key points about Inject[]**:

- Only parameters wrapped with Inject[] are resolved from the container
- Regular parameters can have defaults or be passed as props
- Multiple Inject[] dependencies are supported
- Injected dependencies must be registered in svcs.Registry

Scanning Multiple Packages
---------------------------

You can scan multiple packages in a single call::

    scan_components(
        registry,
        component_registry,
        "myapp.components",
        "myapp.ui.widgets",
        "myapp.admin.components",
    )

Or use ModuleType objects directly::

    import myapp.components
    import myapp.widgets

    scan_components(
        registry,
        component_registry,
        myapp.components,
        myapp.widgets,
    )

String Name Derivation
----------------------

Component string names are always derived from class.__name__::

    @injectable
    @dataclass
    class ButtonComponent:
        pass

    # Registered as "ButtonComponent" in ComponentNameRegistry
    # No override mechanism - name always matches class name

This creates predictable, explicit mappings between component names
and their types.

Error Handling
--------------

**Package not found (fail fast)**::

    # Raises ImportError immediately
    scan_components(registry, cnr, "nonexistent.package")

**Individual module import errors (warn and continue)**::

    # If a module within a package has import errors:
    # - Warning is logged
    # - Scanning continues with other modules
    # - Use logging level WARNING to see these

**Component not found during lookup**::

    lookup = ComponentLookup(container=container)
    try:
        component = lookup("TypoButton", {})
    except ComponentNotFoundError as e:
        # Error includes suggestions based on registered names
        print(e)  # Did you mean: Button, IconButton?

Troubleshooting
---------------

**Component not found during lookup**

If ComponentLookup raises ComponentNotFoundError:

1. Check that scan_components() was called at startup
2. Verify the component class is decorated with @injectable
3. Verify the package containing the component was scanned
4. Check for typos in the component name
5. Use component_registry.get_all_names() to see registered components

**Inject[] dependency not resolved**

If a component's Inject[] dependency is not injected:

1. Verify the dependency is registered in svcs.Registry
2. Check that the type annotation matches the registered type exactly
3. Ensure the dependency is registered before scanning

**Import errors during scanning**

If modules fail to import during scanning:

1. Check the logging output (level WARNING)
2. Fix import errors in individual modules
3. Or exclude problematic modules from scan

Migration Guide
---------------

If you're migrating from manual ComponentNameRegistry.register() calls:

**Before**::

    # Manual registration (old approach)
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()

    from myapp.components import Button, Card

    component_registry.register("Button", Button)
    component_registry.register("Card", Card)
    registry.register_factory(Button, lambda: Button())
    registry.register_factory(Card, lambda: Card())

**After**::

    # Automatic discovery (new approach)
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()

    # In myapp/components.py:
    # @injectable
    # class Button: ...
    #
    # @injectable
    # class Card: ...

    scan_components(
        registry,
        component_registry,
        "myapp.components"
    )

Benefits of automatic discovery:

- No manual registration calls needed
- Components are self-describing via @injectable
- Scanning happens once at startup
- Easy to add new components (just decorate them)
- Type-safe with full IDE support

Thread Safety
-------------

scan_components() uses thread-safe registries:

- ComponentNameRegistry uses threading.Lock internally
- svcs.Registry is thread-safe by design
- scan_components() should be called during single-threaded startup
- No additional synchronization needed

Multiple calls to scan_components() are safe (idempotent), but not
recommended. Call once at application startup.

Complete Example
----------------

::

    from dataclasses import dataclass
    import svcs
    from svcs_di import Inject
    from svcs_di.injectors.decorators import injectable
    from svcs_di.injectors.locator import HopscotchInjector
    from tdom_svcs import ComponentNameRegistry, scan_components
    from tdom_svcs.services.component_lookup import ComponentLookup

    # Define services
    class DatabaseService:
        def get_user(self, user_id: int) -> dict:
            return {"id": user_id, "name": "Alice"}

    # Define components
    @injectable
    @dataclass
    class UserProfile:
        user_id: int = 1
        db: Inject[DatabaseService] = None

        def __call__(self) -> str:
            user = self.db.get_user(self.user_id)
            return f"<div>User: {user['name']}</div>"

    # Application startup
    def setup_app():
        registry = svcs.Registry()
        component_registry = ComponentNameRegistry()

        # Register services
        db = DatabaseService()
        registry.register_value(DatabaseService, db)

        # Scan for components
        scan_components(registry, component_registry, __name__)

        # Setup container
        container = svcs.Container(registry)
        registry.register_value(ComponentNameRegistry, component_registry)
        registry.register_factory(HopscotchInjector, HopscotchInjector)

        # Create lookup
        lookup = ComponentLookup(container=container)
        return lookup

    # Usage
    lookup = setup_app()
    component = lookup("UserProfile", {})
    html = component()  # "<div>User: Alice</div>"

See Also
--------

- svcs_di.injectors.locator.scan: Underlying scan implementation
- svcs_di.injectors.decorators.injectable: Decorator for marking components
- ComponentNameRegistry: String name -> type mapping
- ComponentLookup: Component resolution service
"""

import importlib
import logging
from types import ModuleType
from typing import Any

import svcs
from svcs_di.injectors.locator import (
    _collect_decorated_items,
    _discover_all_modules,
    scan,
)

from tdom_svcs.services.component_registry.component_name_registry import (
    ComponentNameRegistry,
)

__all__ = ["scan_components"]

log = logging.getLogger("tdom_svcs.scanning")


def scan_components(
    registry: svcs.Registry,
    component_name_registry: ComponentNameRegistry,
    *packages: str | ModuleType,
) -> None:
    """
    Scan packages for @injectable decorated classes and register them.

    This function discovers classes decorated with @injectable and performs
    dual registration:
    1. Registers to svcs.Registry (type-based lookup with dependency injection)
    2. Registers to ComponentNameRegistry (string name lookup using class.__name__)

    The function leverages svcs-di's scan() infrastructure for package traversal,
    module discovery, and type-based registration. After svcs-di's scan completes,
    it extracts the discovered classes and registers them by string name in the
    ComponentNameRegistry.

    Args:
        registry: svcs.Registry to register components for type-based DI
        component_name_registry: ComponentNameRegistry to register string names
        *packages: Package/module references to scan:
                   - String names: "myapp.components" (auto-imported)
                   - ModuleType objects: already imported modules
                   - Multiple packages supported: scan(reg, cnr, "app.models", "app.views")

    Returns:
        None (performs side effects by registering to both registries)

    Raises:
        ImportError: If a specified package doesn't exist (fail fast)

    Error Handling:
        - Package not found: Raises ImportError immediately (fail fast)
        - Individual module import errors: Logged as warnings, scanning continues

    Examples:
        >>> import svcs
        >>> from tdom_svcs import ComponentNameRegistry, scan_components
        >>>
        >>> registry = svcs.Registry()
        >>> component_registry = ComponentNameRegistry()
        >>>
        >>> # Scan single package
        >>> scan_components(registry, component_registry, "myapp.components")
        >>>
        >>> # Scan multiple packages
        >>> scan_components(
        ...     registry,
        ...     component_registry,
        ...     "myapp.components",
        ...     "myapp.widgets",
        ... )
        >>>
        >>> # Create container and use components
        >>> container = svcs.Container(registry)
        >>> component_type = component_registry.get_type("Button")
        >>> instance = container.get(component_type)

    See Also:
        - svcs_di.injectors.locator.scan: Underlying scan implementation
        - svcs_di.injectors.decorators.injectable: Decorator for marking components
        - ComponentNameRegistry: String name -> type mapping
    """
    # Step 0: Validate that all string package names can be imported (fail fast)
    # We do this before calling svcs-di's scan() to fail fast on missing packages
    modules_to_scan: list[ModuleType] = []
    for pkg in packages:
        if isinstance(pkg, str):
            # Try to import the package - fail fast if it doesn't exist
            try:
                module = importlib.import_module(pkg)
                modules_to_scan.append(module)
            except ImportError as e:
                # Fail fast: Re-raise ImportError immediately
                log.error(f"Package '{pkg}' not found: {e}")
                raise ImportError(f"Package '{pkg}' not found: {e}") from e
        elif isinstance(pkg, ModuleType):
            modules_to_scan.append(pkg)
        else:
            log.warning(
                f"Invalid package type: {type(pkg)}. Must be str or ModuleType"
            )

    # Step 1: Use svcs-di's scan() to register components to svcs.Registry
    # This handles module discovery and type-based registration
    # with support for resource/location metadata
    # We pass the validated ModuleType objects instead of string names
    # to avoid svcs-di's warn-and-continue behavior
    scan(registry, *modules_to_scan)

    # Step 2: Discover all modules including submodules
    discovered_modules = _discover_all_modules(modules_to_scan)

    # Step 3: Collect @injectable decorated classes from discovered modules
    decorated_items: list[tuple[type, dict[str, Any]]] = _collect_decorated_items(
        discovered_modules
    )

    # Step 4: Register each discovered class to ComponentNameRegistry by string name
    for cls, metadata in decorated_items:
        # Validate it's a class (should always be true due to @injectable validation)
        if not isinstance(cls, type):
            log.warning(
                f"Skipping non-class decorated item: {cls}. "
                f"Only classes can be registered by name."
            )
            continue

        # Use class.__name__ as the string name (no override mechanism)
        name = cls.__name__
        try:
            component_name_registry.register(name, cls)
            log.debug(
                f"Registered component '{name}' -> {cls.__module__}.{cls.__qualname__}"
            )
        except TypeError as e:
            # ComponentNameRegistry validation failed
            log.warning(f"Failed to register '{name}': {e}")
            continue
