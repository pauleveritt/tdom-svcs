"""Implementation of component lookup service."""

import difflib
import inspect
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Callable

import svcs
from svcs_di.injectors.keyword import KeywordAsyncInjector, KeywordInjector

from tdom_svcs.services.component_registry import ComponentNameRegistry

from .exceptions import (
    ComponentNotFoundError,
    InjectorNotFoundError,
    RegistryNotSetupError,
)


@dataclass
class ComponentLookup:
    """
    Service for looking up and constructing components by name.

    ComponentLookup bridges tdom's component system with svcs container by:
    1. Looking up component types by string name using ComponentNameRegistry
    2. Retrieving the appropriate injector (sync or async) from the container
    3. Using the injector to construct component instances with dependencies

    This implementation satisfies the ComponentLookup protocol through structural
    typing without requiring inheritance.

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
    ) -> Callable | None:
        """
        Look up a component by name and construct it with dependency injection.

        This method implements the component resolution workflow:
        1. Retrieve ComponentNameRegistry from container
        2. Look up component type by name
        3. Detect if component is async
        4. Retrieve appropriate injector (sync or async)
        5. Construct component using injector

        Args:
            name: The string name of the component to resolve
            context: Context mapping for service resolution (available for future use)

        Returns:
            A constructed component callable, or None if component not found

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
            # Generate suggestions using fuzzy matching
            all_names = registry.get_all_names()
            suggestions = difflib.get_close_matches(name, all_names, n=5, cutoff=0.6)
            raise ComponentNotFoundError(name, suggestions)

        # Step 3: Detect if component is async
        is_async = inspect.iscoroutinefunction(component_type)

        # Step 4 & 5: Retrieve injector and construct component
        if is_async:
            return self._construct_async_component(component_type)
        else:
            return self._construct_sync_component(component_type)

    def _construct_sync_component(self, component_type: type | Callable) -> Callable:
        """
        Construct a synchronous component using KeywordInjector.

        Args:
            component_type: The component type to construct

        Returns:
            The constructed component instance

        Raises:
            InjectorNotFoundError: If KeywordInjector not in container
        """
        try:
            injector = self.container.get(KeywordInjector)
        except svcs.exceptions.ServiceNotFoundError:
            raise InjectorNotFoundError("KeywordInjector", is_async=False)

        result: Callable = injector(component_type)  # type: ignore[arg-type]
        return result

    def _construct_async_component(self, component_type: type | Callable) -> Callable:
        """
        Construct an asynchronous component using KeywordAsyncInjector.

        Args:
            component_type: The async component type to construct

        Returns:
            The constructed async component instance

        Raises:
            InjectorNotFoundError: If KeywordAsyncInjector not in container
        """
        try:
            injector = self.container.get(KeywordAsyncInjector)
        except svcs.exceptions.ServiceNotFoundError:
            raise InjectorNotFoundError("KeywordAsyncInjector", is_async=True)

        result: Callable = injector(component_type)  # type: ignore[arg-type, assignment]
        return result
