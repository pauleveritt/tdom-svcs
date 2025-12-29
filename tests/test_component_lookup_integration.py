"""
Integration tests for ComponentLookup with scan_components().

This module tests the end-to-end workflow where @injectable decorated
components are discovered via scan_components() and then resolved via
ComponentLookup service. This tests the complete two-stage resolution:
1. String name -> component type (via ComponentNameRegistry)
2. Component type -> component instance (via svcs container and injector)
"""

from dataclasses import dataclass
from pathlib import PurePath

import pytest
import svcs
from svcs_di import Inject
from svcs_di.injectors.decorators import injectable
from svcs_di.injectors.locator import HopscotchAsyncInjector, HopscotchInjector

from tdom_svcs import ComponentNameRegistry, scan_components
from tdom_svcs.services.component_lookup import (
    ComponentLookup,
    ComponentNotFoundError,
)


# Service fixture - used for dependency injection tests
class DatabaseService:
    """Mock database service for testing dependency injection."""

    def get_data(self) -> str:
        return "Data from DB"


# Test fixtures - injectable components for scanning
@injectable
@dataclass
class ScannedButton:
    """Simple component discovered by scanning."""

    label: str = "Click"
    disabled: bool = False

    def __call__(self) -> str:
        disabled_attr = " disabled" if self.disabled else ""
        return f"<button{disabled_attr}>{self.label}</button>"


@injectable
@dataclass
class ComponentWithInjection:
    """Component with Inject[] dependencies from container."""

    db: Inject[DatabaseService]  # Injected from container
    title: str = "Default Title"  # Default value so it's optional

    def __call__(self) -> str:
        data = self.db.get_data()
        return f"<div><h1>{self.title}</h1><p>{data}</p></div>"


@injectable(resource=str)
@dataclass
class ResourceBasedComponent:
    """Component registered with resource metadata."""

    message: str = "Resource component"

    def __call__(self) -> str:
        return f"<p>{self.message}</p>"


@injectable(location=PurePath("/admin"))
@dataclass
class LocationBasedComponent:
    """Component registered with location metadata."""

    path: str = "/admin"

    def __call__(self) -> str:
        return f"<div>Admin at {self.path}</div>"


@injectable
@dataclass
class AsyncScannedComponent:
    """Async component discovered by scanning."""

    message: str = "Async"

    async def __call__(self) -> str:
        return f"<div>{self.message}</div>"


def test_component_lookup_resolves_scanned_component_by_name():
    """Test ComponentLookup resolves scanned components by string name."""
    # Setup registries and container
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()
    container = svcs.Container(registry)

    # Scan this test module for @injectable components
    scan_components(registry, component_registry, __name__)

    # Setup ComponentNameRegistry and injector in container
    registry.register_value(ComponentNameRegistry, component_registry)
    registry.register_factory(HopscotchInjector, HopscotchInjector)

    # Create ComponentLookup
    lookup = ComponentLookup(container=container)

    # Resolve scanned component by string name
    context = {}
    component = lookup("ScannedButton", context)

    # Verify successful resolution
    assert component is not None
    assert isinstance(component, ScannedButton)
    assert component.label == "Click"
    assert component.disabled is False


def test_two_stage_resolution_name_to_type_to_instance():
    """Test two-stage resolution: name->type (ComponentNameRegistry), type->instance (svcs)."""
    # Setup registries and container
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()
    container = svcs.Container(registry)

    # Scan this test module
    scan_components(registry, component_registry, __name__)

    # Setup container dependencies
    registry.register_value(ComponentNameRegistry, component_registry)
    registry.register_factory(HopscotchInjector, HopscotchInjector)

    # Create ComponentLookup
    lookup = ComponentLookup(container=container)

    # Stage 1: ComponentLookup uses ComponentNameRegistry to resolve name->type
    component_type = component_registry.get_type("ScannedButton")
    assert component_type is ScannedButton

    # Stage 2: ComponentLookup uses injector to construct type->instance
    context = {}
    component = lookup("ScannedButton", context)
    assert isinstance(component, ScannedButton)

    # Verify this is a complete end-to-end resolution
    assert component is not None
    assert component.label == "Click"


def test_component_with_inject_dependencies_gets_injected():
    """Test component with Inject[] dependencies gets injected correctly."""
    # Setup registries and container
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()
    container = svcs.Container(registry)

    # Register DatabaseService in container for injection
    db_service = DatabaseService()
    registry.register_value(DatabaseService, db_service)

    # Scan this test module
    scan_components(registry, component_registry, __name__)

    # Setup container dependencies
    registry.register_value(ComponentNameRegistry, component_registry)
    registry.register_factory(HopscotchInjector, HopscotchInjector)

    # Create ComponentLookup
    lookup = ComponentLookup(container=container)

    # Resolve component - db should be injected from container
    context = {}
    component = lookup("ComponentWithInjection", context)

    # Verify injection worked
    assert component is not None
    assert isinstance(component, ComponentWithInjection)
    assert component.db is db_service
    assert component.db.get_data() == "Data from DB"
    # Verify the component works end-to-end
    result = component()
    assert "Default Title" in result
    assert "Data from DB" in result


def test_component_with_resource_metadata_resolved():
    """Test component with resource metadata resolved in correct context."""
    # Setup registries and container
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()
    container = svcs.Container(registry)

    # Scan this test module
    scan_components(registry, component_registry, __name__)

    # Setup container dependencies
    registry.register_value(ComponentNameRegistry, component_registry)
    registry.register_factory(HopscotchInjector, HopscotchInjector)

    # Verify component is registered by string name (regardless of resource metadata)
    assert component_registry.get_type("ResourceBasedComponent") is ResourceBasedComponent

    # Create ComponentLookup
    lookup = ComponentLookup(container=container)

    # Resolve component by name
    context = {}
    component = lookup("ResourceBasedComponent", context)

    # Verify component was resolved
    # Note: Resource-based resolution is handled by svcs container
    # ComponentLookup just ensures the component is discoverable by name
    assert component is not None
    assert isinstance(component, ResourceBasedComponent)


def test_component_with_location_metadata_resolved():
    """Test component with location metadata resolved at correct location."""
    # Setup registries and container
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()
    container = svcs.Container(registry)

    # Scan this test module
    scan_components(registry, component_registry, __name__)

    # Setup container dependencies
    registry.register_value(ComponentNameRegistry, component_registry)
    registry.register_factory(HopscotchInjector, HopscotchInjector)

    # Verify component is registered by string name (regardless of location metadata)
    assert component_registry.get_type("LocationBasedComponent") is LocationBasedComponent

    # Create ComponentLookup
    lookup = ComponentLookup(container=container)

    # Resolve component by name
    context = {}
    component = lookup("LocationBasedComponent", context)

    # Verify component was resolved
    # Note: Location-based resolution is handled by svcs container
    # ComponentLookup just ensures the component is discoverable by name
    assert component is not None
    assert isinstance(component, LocationBasedComponent)
    assert component.path == "/admin"


def test_error_handling_when_component_name_not_found():
    """Test error handling when component name not found."""
    # Setup registries and container
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()
    container = svcs.Container(registry)

    # Scan this test module
    scan_components(registry, component_registry, __name__)

    # Setup container dependencies
    registry.register_value(ComponentNameRegistry, component_registry)
    registry.register_factory(HopscotchInjector, HopscotchInjector)

    # Create ComponentLookup
    lookup = ComponentLookup(container=container)

    # Try to resolve non-existent component
    context = {}
    with pytest.raises(ComponentNotFoundError) as exc_info:
        lookup("NonExistentComponent", context)

    # Verify error message
    error_msg = str(exc_info.value)
    assert "NonExistentComponent" in error_msg


def test_error_raised_for_unknown_scanned_component():
    """Test ComponentNotFoundError raised for unknown component."""
    # Setup registries and container
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()
    container = svcs.Container(registry)

    # Scan this test module - registers ScannedButton, ComponentWithInjection, etc.
    scan_components(registry, component_registry, __name__)

    # Setup container dependencies
    registry.register_value(ComponentNameRegistry, component_registry)
    registry.register_factory(HopscotchInjector, HopscotchInjector)

    # Create ComponentLookup
    lookup = ComponentLookup(container=container)

    # Try to resolve non-existent component
    context = {}
    with pytest.raises(ComponentNotFoundError) as exc_info:
        lookup("NonExistentComponent", context)

    # Verify error message includes component name
    error_msg = str(exc_info.value)
    assert "NonExistentComponent" in error_msg


def test_async_component_with_async_call_method():
    """
    Test async component where __call__ is async.

    ComponentLookup now properly detects async __call__ methods and uses
    HopscotchAsyncInjector for async components. The result is a coroutine
    that needs to be awaited to get the component instance.
    """
    # Setup registries and container
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()
    container = svcs.Container(registry)

    # Scan this test module
    scan_components(registry, component_registry, __name__)

    # Setup container dependencies with BOTH sync and async injectors
    registry.register_value(ComponentNameRegistry, component_registry)
    registry.register_factory(HopscotchInjector, HopscotchInjector)
    registry.register_factory(HopscotchAsyncInjector, HopscotchAsyncInjector)

    # Create ComponentLookup
    lookup = ComponentLookup(container=container)

    # Resolve component - will use async path because __call__ is async
    context = {}
    result = lookup("AsyncScannedComponent", context)

    # Result is a coroutine (because ComponentLookup detected async __call__)
    import inspect
    assert inspect.iscoroutine(result)
    result.close()
