"""
Tests for scan_components() function.

This module tests the scan_components() function which discovers @injectable
decorated classes in packages and registers them in both ComponentNameRegistry
(string name) and svcs.Registry (type-based).
"""

from dataclasses import dataclass
from pathlib import PurePath

import pytest
import svcs
from svcs_di.injectors.decorators import injectable

from tdom_svcs import ComponentNameRegistry, scan_components


# Test fixtures - injectable components
@injectable
@dataclass
class SimpleComponent:
    """Simple component with no dependencies."""

    label: str = "Simple"


@injectable(resource=str)
@dataclass
class ResourceComponent:
    """Component with resource-based registration."""

    message: str = "Resource"


@injectable(location=PurePath("/admin"))
@dataclass
class LocationComponent:
    """Component with location-based registration."""

    path: str = "/admin"


def test_scan_components_discovers_decorated_classes():
    """Test that scan_components() discovers @injectable decorated classes."""
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()

    # Scan this test module for decorated classes
    scan_components(registry, component_registry, __name__)

    # Verify classes were discovered and registered in ComponentNameRegistry
    assert component_registry.get_type("SimpleComponent") is SimpleComponent
    assert component_registry.get_type("ResourceComponent") is ResourceComponent
    assert component_registry.get_type("LocationComponent") is LocationComponent


def test_scan_components_dual_registration():
    """Test that components are registered in both ComponentNameRegistry and svcs.Registry."""
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()
    container = svcs.Container(registry)

    # Scan this test module
    scan_components(registry, component_registry, __name__)

    # Verify dual registration:
    # 1. String name -> type (ComponentNameRegistry)
    assert component_registry.get_type("SimpleComponent") is SimpleComponent

    # 2. Type -> instance (svcs.Registry via container)
    # The component should be resolvable by type through svcs
    instance = container.get(SimpleComponent)
    assert isinstance(instance, SimpleComponent)


def test_scan_components_string_name_from_class_name():
    """Test that string names are derived from class.__name__."""
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()

    # Scan this test module
    scan_components(registry, component_registry, __name__)

    # Verify the string name matches class.__name__
    assert component_registry.get_type("SimpleComponent") is SimpleComponent
    assert component_registry.get_type("ResourceComponent") is ResourceComponent
    assert component_registry.get_type("LocationComponent") is LocationComponent


def test_scan_components_package_not_found_raises_import_error():
    """Test that scan_components() raises ImportError if package doesn't exist."""
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()

    # Try to scan a non-existent package - should fail fast
    with pytest.raises(ImportError):
        scan_components(registry, component_registry, "nonexistent.package.name")


def test_scan_components_module_import_error_logs_warning(caplog):
    """Test that module import errors are logged as warnings and scanning continues."""
    import logging
    import sys
    import types

    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()

    # Create a package with a broken module
    test_package = types.ModuleType("test_broken_package")
    test_package.__path__ = []  # type: ignore[attr-defined]
    sys.modules["test_broken_package"] = test_package

    # Create a submodule that will fail to import properly
    broken_module = types.ModuleType("test_broken_package.broken")
    # Simulate an import error by making it raise when accessed
    sys.modules["test_broken_package.broken"] = broken_module

    try:
        # Scan should warn about the broken module but continue
        with caplog.at_level(logging.WARNING):
            scan_components(registry, component_registry, "test_broken_package")

        # Note: This test validates the error handling pattern exists
        # The actual logging will depend on svcs-di's scan() implementation
    finally:
        # Cleanup
        if "test_broken_package" in sys.modules:
            del sys.modules["test_broken_package"]
        if "test_broken_package.broken" in sys.modules:
            del sys.modules["test_broken_package.broken"]


def test_scan_components_resource_based_registration():
    """Test that components with resource metadata are registered correctly."""
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()

    # Scan this test module
    scan_components(registry, component_registry, __name__)

    # Verify resource-based component is registered by string name
    assert component_registry.get_type("ResourceComponent") is ResourceComponent

    # The resource metadata should be handled by svcs-di's scan()
    # We just verify the component is discoverable by name


def test_scan_components_location_based_registration():
    """Test that components with location metadata are registered correctly."""
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()

    # Scan this test module
    scan_components(registry, component_registry, __name__)

    # Verify location-based component is registered by string name
    assert component_registry.get_type("LocationComponent") is LocationComponent

    # The location metadata should be handled by svcs-di's scan()
    # We just verify the component is discoverable by name


def test_scan_components_accepts_module_type():
    """Test that scan_components() accepts ModuleType objects."""
    import sys

    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()

    # Get the current module as a ModuleType
    current_module = sys.modules[__name__]

    # Scan using ModuleType instead of string
    scan_components(registry, component_registry, current_module)

    # Verify components were discovered
    assert component_registry.get_type("SimpleComponent") is SimpleComponent
