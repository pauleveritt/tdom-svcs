"""Implementation of component lookup service."""

import inspect
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Callable, Coroutine

import svcs
from svcs_di.injectors.locator import HopscotchAsyncInjector, HopscotchInjector

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
    Service for looking up and constructing components by name.

    ComponentLookup bridges tdom's component system with svcs container by:
    1. Looking up component class types by string name using ComponentNameRegistry
    2. Retrieving the appropriate injector (sync or async) from the container
    3. Using the injector to construct component instances with dependencies

    This implementation uses HopscotchInjector (production injector) which supports
    resource-based and location-based component resolution.

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

    def __call__(
        self, name: str, context: Mapping[str, Any]
    ) -> Any:
        """
        Look up a component by name and construct it with dependency injection.

        This method implements the component resolution workflow:
        1. Retrieve ComponentNameRegistry from container
        2. Look up component class type by name
        3. Detect if component is async
        4. Retrieve appropriate injector (sync or async)
        5. Construct component using injector

        Args:
            name: The string name of the component to resolve
            context: Context mapping for service resolution (available for future use)

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
        assert isinstance(component_type, type), f"Expected class, got {type(component_type)}"

        # Step 3: Detect if component is async
        # For class components, check if __call__ method is async
        is_async = (
            hasattr(component_type, "__call__")
            and inspect.iscoroutinefunction(component_type.__call__)
        )

        # Step 4 & 5: Retrieve injector and construct component
        if is_async:
            return self._construct_async_component(component_type)
        else:
            return self._construct_sync_component(component_type)

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
