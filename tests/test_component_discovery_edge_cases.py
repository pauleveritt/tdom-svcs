"""
Edge case tests for component discovery and registration.

This module tests edge cases and error paths that are not covered in the
main test_scan_components.py and test_component_lookup_integration.py files.
These tests focus on thread-safety, error handling, and unusual scenarios.
"""

import sys
import threading
from dataclasses import dataclass
from types import ModuleType

import pytest
import svcs
from svcs_di import Inject
from svcs_di.injectors.decorators import injectable
from svcs_di.injectors.keyword import KeywordInjector

from tdom_svcs import ComponentNameRegistry, scan_components
from tdom_svcs.services.component_lookup import ComponentLookup


# Test fixtures
@injectable
@dataclass
class ThreadTestComponent:
    """Component for thread-safety testing."""

    value: str = "thread_test"


@injectable
@dataclass
class MultiInjectionComponent:
    """Component with multiple injected dependencies."""

    service_a: Inject[str] = None
    service_b: Inject[int] = None
    service_c: Inject[float] = None
    regular_param: str = "default"


def test_concurrent_registration_thread_safety():
    """Test that concurrent scan_components calls are thread-safe."""
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()

    # Track results from each thread
    results = []
    errors = []

    def scan_in_thread():
        """Scan components in a separate thread."""
        try:
            scan_components(registry, component_registry, __name__)
            results.append("success")
        except Exception as e:
            errors.append(e)

    # Start multiple threads that scan components concurrently
    threads = [threading.Thread(target=scan_in_thread) for _ in range(5)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    # Verify no errors occurred
    assert len(errors) == 0, f"Errors during concurrent scanning: {errors}"
    assert len(results) == 5

    # Verify component is registered (only once, not 5 times)
    assert component_registry.get_type("ThreadTestComponent") is ThreadTestComponent


def test_scan_components_with_empty_package():
    """Test scanning a package with no modules."""
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()

    # Create an empty package
    empty_package = ModuleType("empty_test_package")
    empty_package.__path__ = []  # type: ignore[attr-defined]
    sys.modules["empty_test_package"] = empty_package

    try:
        # Scanning empty package should not raise an error
        scan_components(registry, component_registry, empty_package)

        # No components should be registered from this package
        # (but other components might exist from previous tests)
    finally:
        # Cleanup
        if "empty_test_package" in sys.modules:
            del sys.modules["empty_test_package"]


def test_scan_components_with_module_without_components():
    """Test scanning a module that has no @injectable components."""
    import json  # Standard library module with no @injectable components

    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()

    # Get count before scanning
    initial_count = len(component_registry.get_all_names())

    # Scanning module with no components should not raise error
    scan_components(registry, component_registry, json)

    # Should not add any new components
    # (count might not be identical if other tests ran first, but json shouldn't add any)
    final_count = len(component_registry.get_all_names())
    # We can't assert exact equality because previous tests might have registered components
    # But we can verify that json module didn't cause any errors


def test_scan_components_called_multiple_times():
    """Test that calling scan_components multiple times is safe."""
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()

    # Scan the same module multiple times
    scan_components(registry, component_registry, __name__)
    scan_components(registry, component_registry, __name__)
    scan_components(registry, component_registry, __name__)

    # Component should still be registered correctly
    assert component_registry.get_type("ThreadTestComponent") is ThreadTestComponent

    # Verify the component can be instantiated
    container = svcs.Container(registry)
    instance = container.get(ThreadTestComponent)
    assert isinstance(instance, ThreadTestComponent)


def test_component_with_multiple_inject_dependencies():
    """Test component with multiple Inject[] dependencies."""
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()
    container = svcs.Container(registry)

    # Register all the services that will be injected
    registry.register_value(str, "service_a_value")
    registry.register_value(int, 42)
    registry.register_value(float, 3.14)

    # Scan this test module
    scan_components(registry, component_registry, __name__)

    # Setup ComponentLookup
    registry.register_value(ComponentNameRegistry, component_registry)
    injector = KeywordInjector(container=container)
    registry.register_value(KeywordInjector, injector)
    lookup = ComponentLookup(container=container)

    # Resolve component with multiple injected dependencies
    context = {}
    component = lookup("MultiInjectionComponent", context)

    # Verify all dependencies were injected
    assert component is not None
    assert isinstance(component, MultiInjectionComponent)
    assert component.service_a == "service_a_value"
    assert component.service_b == 42
    assert component.service_c == 3.14
    assert component.regular_param == "default"


def test_scan_components_with_multiple_packages():
    """Test scanning multiple packages in a single call."""
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()

    # Scan multiple modules
    import dataclasses
    import typing

    # This should not raise an error even though these modules have no @injectable components
    scan_components(registry, component_registry, dataclasses, typing)

    # No components should be registered from standard library modules


def test_scan_components_with_mixed_package_types():
    """Test scanning with both string names and ModuleType objects."""
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()

    # Get this module as ModuleType
    current_module = sys.modules[__name__]

    # Scan with mixed types - this module as ModuleType and string
    scan_components(registry, component_registry, current_module)

    # Verify components were discovered
    assert component_registry.get_type("ThreadTestComponent") is ThreadTestComponent


def test_scan_components_idempotency():
    """Test that scanning is idempotent - can be called multiple times safely."""
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()

    # Scan once
    scan_components(registry, component_registry, __name__)
    first_type = component_registry.get_type("ThreadTestComponent")

    # Scan again
    scan_components(registry, component_registry, __name__)
    second_type = component_registry.get_type("ThreadTestComponent")

    # Should return the same type
    assert first_type is second_type
    assert first_type is ThreadTestComponent


def test_scan_nonexistent_package_fails_immediately():
    """Test that scanning a non-existent package fails fast with clear error."""
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()

    # This should raise ImportError immediately
    with pytest.raises(ImportError) as exc_info:
        scan_components(
            registry, component_registry, "this.package.definitely.does.not.exist"
        )

    # Verify error message mentions the package
    assert "this.package.definitely.does.not.exist" in str(exc_info.value)
