"""
Consolidated tests for the component lookup and registration system.

This module combines tests from:
- test_component_lookup.py
- test_component_lookup_integration.py
- test_component_discovery_edge_cases.py

Covering:
- Component registration and lookup
- Dependency injection
- Error handling
- Edge cases and thread safety
"""

import inspect
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import pytest
import svcs
from svcs_di import Inject
from svcs_di.injectors.decorators import injectable
from svcs_di.injectors.locator import HopscotchAsyncInjector, HopscotchInjector

from tdom_svcs import ComponentNameRegistry, scan_components
from tdom_svcs.services.component_lookup import (
    ComponentLookup,
    ComponentNotFoundError,
    InjectorNotFoundError,
    RegistryNotSetupError,
)


# Test fixtures
class DatabaseService:
    """Mock database service."""

    def get_data(self) -> str:
        return "Data from DB"


@injectable
@dataclass
class SimpleComponent:
    """Simple component without dependencies."""

    label: str = "Test"

    def __call__(self) -> str:
        return f"<div>{self.label}</div>"


@injectable
@dataclass
class ComponentWithDependency:
    """Component with injected dependency."""

    db: Inject[DatabaseService]
    title: str = "Default"

    def __call__(self) -> str:
        data = self.db.get_data()
        return f"<div>{self.title}: {data}</div>"


@injectable
@dataclass
class AsyncComponent:
    """Async component."""

    message: str = "Async"

    async def __call__(self) -> str:
        return f"<div>{self.message}</div>"


def test_component_lookup_basic():
    """Test basic component registration and lookup."""
    registry = svcs.Registry()
    container = svcs.Container(registry)

    name_registry = ComponentNameRegistry()
    name_registry.register("SimpleComponent", SimpleComponent)
    registry.register_value(ComponentNameRegistry, name_registry)
    registry.register_factory(HopscotchInjector, HopscotchInjector)

    lookup = ComponentLookup(container=container)

    context: Mapping[str, Any] = {}
    component = lookup("SimpleComponent", context)

    assert component is not None
    assert callable(component)
    result = component()
    assert "Test" in result


def test_component_with_dependencies():
    """Test component with injected dependencies."""
    registry = svcs.Registry()
    container = svcs.Container(registry)

    # Register service
    db = DatabaseService()
    registry.register_value(DatabaseService, db)

    # Register component
    name_registry = ComponentNameRegistry()
    name_registry.register("ComponentWithDependency", ComponentWithDependency)
    registry.register_value(ComponentNameRegistry, name_registry)
    registry.register_factory(HopscotchInjector, HopscotchInjector)

    lookup = ComponentLookup(container=container)

    context: Mapping[str, Any] = {}
    component = lookup("ComponentWithDependency", context)
    result = component()

    assert "Data from DB" in result


@pytest.mark.anyio
async def test_async_component():
    """Test async component resolution."""
    registry = svcs.Registry()
    container = svcs.Container(registry)

    name_registry = ComponentNameRegistry()
    name_registry.register("AsyncComponent", AsyncComponent)
    registry.register_value(ComponentNameRegistry, name_registry)
    registry.register_factory(HopscotchAsyncInjector, HopscotchAsyncInjector)

    lookup = ComponentLookup(container=container)

    context: Mapping[str, Any] = {}
    component_coro = lookup("AsyncComponent", context)

    # Async components return a coroutine
    assert inspect.iscoroutine(component_coro)
    component = await component_coro
    result = await component()
    assert "Async" in result


def test_component_not_found_error():
    """Test error when component not found."""
    registry = svcs.Registry()
    container = svcs.Container(registry)

    name_registry = ComponentNameRegistry()
    registry.register_value(ComponentNameRegistry, name_registry)
    registry.register_factory(HopscotchInjector, HopscotchInjector)

    lookup = ComponentLookup(container=container)

    context: Mapping[str, Any] = {}
    with pytest.raises(ComponentNotFoundError) as exc_info:
        lookup("NonExistent", context)

    assert "NonExistent" in str(exc_info.value)


def test_registry_not_setup_error():
    """Test error when ComponentNameRegistry not registered."""
    registry = svcs.Registry()
    container = svcs.Container(registry)
    registry.register_factory(HopscotchInjector, HopscotchInjector)

    lookup = ComponentLookup(container=container)

    context: Mapping[str, Any] = {}
    with pytest.raises(RegistryNotSetupError):
        lookup("SomeComponent", context)


def test_injector_not_found_error():
    """Test error when injector not registered."""
    registry = svcs.Registry()
    container = svcs.Container(registry)

    name_registry = ComponentNameRegistry()
    name_registry.register("SimpleComponent", SimpleComponent)
    registry.register_value(ComponentNameRegistry, name_registry)

    lookup = ComponentLookup(container=container)

    context: Mapping[str, Any] = {}
    with pytest.raises(InjectorNotFoundError):
        lookup("SimpleComponent", context)


def test_scan_components_integration():
    """Test component scanning integration."""
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()

    # Scan this test module
    scan_components(registry, component_registry, __name__)

    # Verify components were registered
    assert component_registry.get_type("SimpleComponent") is not None
    assert component_registry.get_type("ComponentWithDependency") is not None


def test_scan_components_idempotency():
    """Test that scanning multiple times doesn't cause issues."""
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()

    scan_components(registry, component_registry, __name__)
    scan_components(registry, component_registry, __name__)

    # Should still work
    assert component_registry.get_type("SimpleComponent") is not None


def test_component_name_registry_thread_safety():
    """Test thread-safe component registration."""
    import threading

    registry = ComponentNameRegistry()
    errors = []

    def register_component(name: str):
        try:
            registry.register(name, SimpleComponent)
            result = registry.get_type(name)
            if result is None:
                errors.append(f"Failed to get {name}")
        except Exception as e:
            errors.append(str(e))

    threads = [
        threading.Thread(target=register_component, args=(f"Component{i}",))
        for i in range(10)
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(errors) == 0


def test_async_component_without_async_injector():
    """Test error when async component requested without async injector."""
    registry = svcs.Registry()
    container = svcs.Container(registry)

    name_registry = ComponentNameRegistry()
    name_registry.register("AsyncComponent", AsyncComponent)
    registry.register_value(ComponentNameRegistry, name_registry)
    registry.register_factory(HopscotchInjector, HopscotchInjector)  # Wrong injector

    lookup = ComponentLookup(container=container)

    context: Mapping[str, Any] = {}
    with pytest.raises(InjectorNotFoundError) as exc_info:
        lookup("AsyncComponent", context)

    assert "async" in str(exc_info.value).lower() or "AsyncInjector" in str(
        exc_info.value
    )
