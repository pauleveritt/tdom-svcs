"""
Tests for ComponentLookup service.

This module tests the ComponentLookup service which resolves component names
to callable components using dependency injection.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import pytest
import svcs
from svcs_di import Inject

from svcs_di.injectors.locator import HopscotchAsyncInjector, HopscotchInjector
from tdom_svcs.services.component_lookup import (
    ComponentLookup,
    ComponentLookupProtocol,
    ComponentNotFoundError,
    InjectorNotFoundError,
    RegistryNotSetupError,
)
from tdom_svcs.services.component_registry import ComponentNameRegistry


# Test fixtures - simple component types
@dataclass
class ButtonComponent:
    """Dataclass-based button component with dependencies."""

    label: str = "Click"
    disabled: bool = False

    def __call__(self) -> str:
        """Render the button."""
        disabled_attr = " disabled" if self.disabled else ""
        return f"<button{disabled_attr}>{self.label}</button>"


@dataclass
class CardComponent:
    """Class-based card component."""

    title: str = "Card"
    content: str = "Content"

    def __call__(self) -> str:
        return f"<div><h2>{self.title}</h2><p>{self.content}</p></div>"


@dataclass
class AsyncAlertComponent:
    """Async class-based alert component."""

    message: str = "Alert"
    level: str = "info"

    async def __call__(self) -> str:
        return f"<div class='alert-{self.level}'>{self.message}</div>"


@dataclass
class ComponentWithDependency:
    """Component that depends on a service from container."""

    message: str = "Default"

    def __call__(self) -> str:
        return f"<p>{self.message}</p>"


def test_component_lookup_satisfies_protocol():
    """Test that ComponentLookup satisfies ComponentLookupProtocol through structural typing."""
    # Create container
    registry = svcs.Registry()
    container = svcs.Container(registry)

    # Create ComponentLookup instance
    lookup = ComponentLookup(container=container)

    # Verify it satisfies the protocol via structural typing
    assert isinstance(lookup, ComponentLookupProtocol)


def test_resolve_sync_component_by_name():
    """Test successful resolution of sync component by name."""
    # Setup container with registry and injector
    registry = svcs.Registry()
    container = svcs.Container(registry)

    # Register ComponentNameRegistry
    name_registry = ComponentNameRegistry()
    name_registry.register("Button", ButtonComponent)
    registry.register_value(ComponentNameRegistry, name_registry)

    # Register HopscotchInjector factory
    registry.register_factory(HopscotchInjector, HopscotchInjector)

    # Create ComponentLookup
    lookup = ComponentLookup(container=container)

    # Resolve component
    context: Mapping[str, Any] = {}
    component = lookup("Button", context)

    # Verify result
    assert component is not None
    assert isinstance(component, ButtonComponent)
    assert component.label == "Click"
    assert component.disabled is False


def test_resolve_async_component_by_name():
    """Test successful resolution of async component by name."""
    # Setup container with registry and async injector
    registry = svcs.Registry()
    container = svcs.Container(registry)

    # Register ComponentNameRegistry
    name_registry = ComponentNameRegistry()
    name_registry.register("Alert", AsyncAlertComponent)
    registry.register_value(ComponentNameRegistry, name_registry)

    # Register HopscotchAsyncInjector factory
    registry.register_factory(HopscotchAsyncInjector, HopscotchAsyncInjector)

    # Create ComponentLookup
    lookup = ComponentLookup(container=container)

    # Resolve async component - returns a coroutine that needs to be awaited
    context: Mapping[str, Any] = {}
    result = lookup("Alert", context)

    # The result is a coroutine (awaitable), which is what we expect
    import inspect
    assert inspect.iscoroutine(result)
    # Clean up the coroutine to avoid warning
    result.close()


def test_raise_error_when_registry_not_found():
    """Test that RegistryNotSetupError is raised when registry not in container."""
    # Create container WITHOUT ComponentNameRegistry
    registry = svcs.Registry()
    container = svcs.Container(registry)

    # Register injector (but not registry)
    registry.register_factory(HopscotchInjector, HopscotchInjector)

    # Create ComponentLookup
    lookup = ComponentLookup(container=container)

    # Try to resolve - should raise RegistryNotSetupError
    context: Mapping[str, Any] = {}
    with pytest.raises(RegistryNotSetupError) as exc_info:
        lookup("Button", context)

    # Verify error message includes helpful guidance
    error_msg = str(exc_info.value)
    assert "ComponentNameRegistry" in error_msg
    assert "setup_container()" in error_msg


def test_raise_error_when_injector_not_found():
    """Test that InjectorNotFoundError is raised when injector not in container."""
    # Create container with registry but WITHOUT injector
    registry = svcs.Registry()
    container = svcs.Container(registry)

    # Register ComponentNameRegistry
    name_registry = ComponentNameRegistry()
    name_registry.register("Button", ButtonComponent)
    registry.register_value(ComponentNameRegistry, name_registry)

    # Do NOT register injector

    # Create ComponentLookup
    lookup = ComponentLookup(container=container)

    # Try to resolve - should raise InjectorNotFoundError
    context: Mapping[str, Any] = {}
    with pytest.raises(InjectorNotFoundError) as exc_info:
        lookup("Button", context)

    # Verify error message includes helpful guidance
    error_msg = str(exc_info.value)
    assert "HopscotchInjector" in error_msg or "injector" in error_msg.lower()
    assert "setup_container()" in error_msg or "register" in error_msg.lower()


def test_raise_error_when_component_not_found():
    """Test that ComponentNotFoundError is raised for unknown component."""
    # Setup container with registry and injector
    registry = svcs.Registry()
    container = svcs.Container(registry)

    # Register ComponentNameRegistry with some components
    name_registry = ComponentNameRegistry()
    name_registry.register("Button", ButtonComponent)
    name_registry.register("Card", CardComponent)
    name_registry.register("Alert", AsyncAlertComponent)
    registry.register_value(ComponentNameRegistry, name_registry)

    # Register HopscotchInjector factory
    registry.register_factory(HopscotchInjector, HopscotchInjector)

    # Create ComponentLookup
    lookup = ComponentLookup(container=container)

    # Try to resolve non-existent component - should raise ComponentNotFoundError
    context: Mapping[str, Any] = {}
    with pytest.raises(ComponentNotFoundError) as exc_info:
        lookup("UnknownComponent", context)

    # Verify error message includes component name
    error_msg = str(exc_info.value)
    assert "UnknownComponent" in error_msg


def test_resolve_component_with_container_dependencies():
    """Test resolving component that has dependencies from container."""
    # Setup container with registry and injector
    registry = svcs.Registry()
    container = svcs.Container(registry)

    # Register a service that the component depends on
    registry.register_value(str, "Hello from container!")

    # Create component that depends on str - must use Inject[str] to inject from container
    @dataclass
    class DependentComponent:
        message: Inject[str]  # Will be injected from container

        def __call__(self) -> str:
            return f"<p>{self.message}</p>"

    # Register ComponentNameRegistry
    name_registry = ComponentNameRegistry()
    name_registry.register("Dependent", DependentComponent)
    registry.register_value(ComponentNameRegistry, name_registry)

    # Register HopscotchInjector factory
    registry.register_factory(HopscotchInjector, HopscotchInjector)

    # Create ComponentLookup
    lookup = ComponentLookup(container=container)

    # Resolve component - injector should resolve dependencies
    context: Mapping[str, Any] = {}
    component = lookup("Dependent", context)

    # Verify result - component should have injected dependency
    assert component is not None
    assert isinstance(component, DependentComponent)
    # Verify the injected value
    assert component.message == "Hello from container!"


def test_async_component_without_async_injector():
    """Test that async component without AsyncInjector raises helpful error."""
    # Setup container with registry and SYNC injector only
    registry = svcs.Registry()
    container = svcs.Container(registry)

    # Register ComponentNameRegistry with async component
    name_registry = ComponentNameRegistry()
    name_registry.register("Alert", AsyncAlertComponent)
    registry.register_value(ComponentNameRegistry, name_registry)

    # Register ONLY HopscotchInjector (not async)
    registry.register_factory(HopscotchInjector, HopscotchInjector)

    # Create ComponentLookup
    lookup = ComponentLookup(container=container)

    # Try to resolve async component - should raise InjectorNotFoundError
    context: Mapping[str, Any] = {}
    with pytest.raises(InjectorNotFoundError) as exc_info:
        lookup("Alert", context)

    # Verify error message mentions async injector
    error_msg = str(exc_info.value)
    assert "async" in error_msg.lower() or "AsyncInjector" in error_msg
