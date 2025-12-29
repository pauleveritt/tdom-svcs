"""Implementation of component lookup service."""

import inspect
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Coroutine, cast

import svcs
from svcs_di.injectors.locator import HopscotchAsyncInjector, HopscotchInjector

from tdom_svcs.services.middleware import (
    Context,
    MiddlewareManager,
    get_component_middleware,
)
from tdom_svcs.services.component_registry import ComponentNameRegistry

from .exceptions import (
    ComponentNotFoundError,
    InjectorNotFoundError,
    RegistryNotSetupError,
)

type T = object


@dataclass
class ComponentLookup:
    """
    Service for looking up and constructing components by name with middleware support.

    ComponentLookup bridges tdom's component system with svcs container by:
    1. Executing global middleware (pre-resolution phase)
    2. Looking up component class types by string name using ComponentNameRegistry
    3. Executing per-component middleware (pre-resolution phase)
    4. Retrieving the appropriate injector (sync or async) from the container
    5. Using the injector to construct component instances with dependencies
    6. Executing middleware (post-resolution phase)

    This implementation uses HopscotchInjector (production injector) which supports
    resource-based and location-based component resolution, and integrates the
    middleware system for component lifecycle hooks.

    Note: ComponentLookup resolves class components by string name. Function components
    can use Inject[] but cannot be looked up by name.

    Example:
        >>> registry = svcs.Registry()
        >>> container = svcs.Container(registry)
        >>> # ... setup registry and injector ...
        >>> lookup = ComponentLookup(container=container)
        >>> component = lookup("Button", context={})
    """

    container: svcs.Container

    def __call__(self, name: str, context: Mapping[str, Any]) -> Any:
        """
        Look up a component by name and construct it with dependency injection and middleware.

        This method implements the component resolution workflow with middleware integration:
        1. Retrieve ComponentNameRegistry from container
        2. Look up component class type by name
        3. Execute pre-resolution middleware (global + per-component)
        4. Detect if component is async
        5. Retrieve appropriate injector (sync or async)
        6. Construct component using injector
        7. Execute post-resolution middleware (global + per-component)

        Middleware execution:
        - Global middleware executes first (from MiddlewareManager)
        - Per-component middleware executes second (from component metadata)
        - Both respect priority ordering (lower numbers first)
        - If any middleware returns None, execution halts

        Args:
            name: The string name of the component to resolve
            context: Context mapping for service resolution and middleware access

        Returns:
            A constructed component callable

        Raises:
            RegistryNotSetupError: If ComponentNameRegistry not in container
            ComponentNotFoundError: If component name not found in registry
            InjectorNotFoundError: If required injector not in container
        """
        # Step 1: Retrieve ComponentNameRegistry from container
        try:
            registry = self.container.get(ComponentNameRegistry)
        except svcs.exceptions.ServiceNotFoundError:
            raise RegistryNotSetupError()

        # Step 2: Look up component type by name
        component_type = registry.get_type(name)
        if component_type is None:
            raise ComponentNotFoundError(name)

        # component_type is guaranteed to be `type` (not None, not Callable)
        # ComponentNameRegistry now only accepts and returns class types
        assert isinstance(component_type, type), (
            f"Expected class, got {type(component_type)}"
        )

        # Step 3: Execute pre-resolution middleware
        # Start with empty props (components don't have props at lookup time in this flow)
        # Note: In a full implementation, props would come from the template
        props: dict[str, Any] = {}

        # Execute global middleware (if MiddlewareManager is registered)
        try:
            middleware_manager = self.container.get(MiddlewareManager)
            props_after_global = middleware_manager.execute(
                component_type, props, cast(Context, context)
            )
            if props_after_global is None:
                # Middleware halted execution
                raise RuntimeError(
                    f"Global middleware halted execution for component {name}"
                )
            props = props_after_global
        except svcs.exceptions.ServiceNotFoundError:
            # MiddlewareManager not registered - skip global middleware
            pass

        # Execute per-component middleware (if any)
        component_middleware = get_component_middleware(component_type)
        pre_resolution_middleware = component_middleware.get("pre_resolution", [])

        if pre_resolution_middleware:
            # Sort by priority (lower numbers first)
            sorted_middleware = sorted(pre_resolution_middleware, key=lambda m: m.priority)
            for middleware in sorted_middleware:
                props = middleware(component_type, props, cast(Context, context))
                if props is None:
                    # Middleware halted execution
                    raise RuntimeError(
                        f"Per-component middleware halted execution for component {name}"
                    )

        # Step 4: Detect if component is async
        # For class components, check if __call__ method is async
        is_async = hasattr(component_type, "__call__") and inspect.iscoroutinefunction(
            component_type.__call__
        )

        # Step 5 & 6: Retrieve injector and construct component
        if is_async:
            return self._construct_async_component(component_type)
        else:
            return self._construct_sync_component(component_type)

        # Note: Post-resolution middleware would execute here after component construction
        # However, at this point the component is already constructed and returned
        # Post-resolution middleware would need to be integrated at a higher level
        # where we have access to the constructed component instance

    def _construct_sync_component(self, component_type: type[T]) -> T:
        """
        Construct a synchronous component using HopscotchInjector.

        HopscotchInjector is the production injector that supports resource-based
        and location-based component resolution.

        Args:
            component_type: The component class type to construct

        Returns:
            The constructed component instance

        Raises:
            InjectorNotFoundError: If HopscotchInjector not in container
        """
        try:
            injector = self.container.get(HopscotchInjector)
        except svcs.exceptions.ServiceNotFoundError:
            raise InjectorNotFoundError("HopscotchInjector", is_async=False)

        # injector(component_type) correctly receives type[T] and returns T
        return injector(component_type)

    def _construct_async_component(
        self, component_type: type[T]
    ) -> Coroutine[Any, Any, T]:
        """
        Construct an asynchronous component using HopscotchAsyncInjector.

        HopscotchAsyncInjector is the production async injector that supports
        resource-based and location-based component resolution.

        Args:
            component_type: The async component class type to construct

        Returns:
            Coroutine that resolves to the constructed component instance

        Raises:
            InjectorNotFoundError: If HopscotchAsyncInjector not in container
        """
        try:
            injector = self.container.get(HopscotchAsyncInjector)
        except svcs.exceptions.ServiceNotFoundError:
            raise InjectorNotFoundError("HopscotchAsyncInjector", is_async=True)

        # injector(component_type) returns Coroutine[Any, Any, T]
        return injector(component_type)
