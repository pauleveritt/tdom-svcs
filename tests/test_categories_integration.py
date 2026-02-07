"""Tests for injectable categories integration.

This module verifies that @middleware and @component decorators correctly
use svcs-di's injectable categories system instead of custom metadata attributes.
"""

from dataclasses import dataclass

import pytest
from svcs_di.injectors import HopscotchRegistry

from tdom_svcs import component, middleware, scan
from tdom_svcs.services.middleware.decorators import COMPONENT_MIDDLEWARE_ATTR


@dataclass
class SampleMiddleware:
    """Sample middleware for category verification."""

    priority: int = 0

    def __call__(self, component, props, context):
        return props


@dataclass
class AnotherMiddleware:
    """Another sample middleware."""

    priority: int = 10

    def __call__(self, component, props, context):
        return props


@dataclass
class SampleComponent:
    """Sample component for category verification."""

    value: str = "test"


def test_middleware_sets_category_not_metadata_attr():
    """Verify @middleware sets categories in metadata, not custom attribute."""

    @middleware
    @dataclass
    class MyMiddleware:
        priority: int = 0

        def __call__(self, component, props, context):
            return props

    # Should have injectable metadata with categories
    assert hasattr(MyMiddleware, "__injectable_metadata__")
    metadata = MyMiddleware.__injectable_metadata__
    assert "middleware" in metadata["categories"]

    # Should NOT have old _tdom_middleware_ attribute
    assert not hasattr(MyMiddleware, "_tdom_middleware_")


def test_component_sets_category_and_middleware_attr():
    """Verify @component sets categories AND middleware attribute."""

    @component
    @dataclass
    class MyComponent:
        value: str = "test"

    # Should have injectable metadata with categories
    assert hasattr(MyComponent, "__injectable_metadata__")
    metadata = MyComponent.__injectable_metadata__
    assert "component" in metadata["categories"]

    # Should have component middleware attribute (empty dict for bare decorator)
    assert hasattr(MyComponent, COMPONENT_MIDDLEWARE_ATTR)
    assert getattr(MyComponent, COMPONENT_MIDDLEWARE_ATTR) == {}


def test_component_with_middleware_config():
    """Verify @component(middleware={...}) stores middleware config."""

    @component(middleware={"pre_resolution": [SampleMiddleware]})
    @dataclass
    class MyComponent:
        value: str = "test"

    # Should have injectable metadata with categories
    assert hasattr(MyComponent, "__injectable_metadata__")
    metadata = MyComponent.__injectable_metadata__
    assert "component" in metadata["categories"]

    # Should have middleware config stored
    mw_config = getattr(MyComponent, COMPONENT_MIDDLEWARE_ATTR)
    assert "pre_resolution" in mw_config
    assert SampleMiddleware in mw_config["pre_resolution"]


def test_scan_discovers_middleware_by_category():
    """Verify scan() discovers middleware via categories."""

    @middleware
    @dataclass
    class ScanSampleMiddleware:
        priority: int = 0

        def __call__(self, component, props, context):
            return props

    registry = HopscotchRegistry()
    scan(registry, locals_dict=locals())

    # Should be discoverable via category
    middleware_types = list(registry.get_by_category("middleware"))
    assert ScanSampleMiddleware in middleware_types


def test_scan_discovers_components_by_category():
    """Verify scan() discovers components via categories."""

    @component
    @dataclass
    class ScanTestComponent:
        value: str = "test"

    registry = HopscotchRegistry()
    scan(registry, locals_dict=locals())

    # Should be discoverable via category
    component_types = list(registry.get_by_category("component"))
    assert ScanTestComponent in component_types


def test_scan_registers_component_middleware():
    """Verify scan() registers component middleware configurations."""

    @component(middleware={"pre_resolution": [SampleMiddleware]})
    @dataclass
    class ConfiguredComponent:
        value: str = "test"

    registry = HopscotchRegistry()
    scan(registry, locals_dict=locals())

    # Component should be registered with middleware config
    mw_config = getattr(ConfiguredComponent, COMPONENT_MIDDLEWARE_ATTR, {})
    assert "pre_resolution" in mw_config
    assert SampleMiddleware in mw_config["pre_resolution"]


def test_multiple_middleware_discovery():
    """Verify multiple middleware can be discovered in single scan."""

    @middleware
    @dataclass
    class FirstMiddleware:
        priority: int = 0

        def __call__(self, component, props, context):
            return props

    @middleware
    @dataclass
    class SecondMiddleware:
        priority: int = 10

        def __call__(self, component, props, context):
            return props

    registry = HopscotchRegistry()
    scan(registry, locals_dict=locals())

    middleware_types = list(registry.get_by_category("middleware"))
    assert FirstMiddleware in middleware_types
    assert SecondMiddleware in middleware_types
    assert len([m for m in middleware_types if m in (FirstMiddleware, SecondMiddleware)]) == 2


def test_multiple_components_discovery():
    """Verify multiple components can be discovered in single scan."""

    @component
    @dataclass
    class FirstComponent:
        value: str = "first"

    @component(middleware={"pre_resolution": [SampleMiddleware]})
    @dataclass
    class SecondComponent:
        value: str = "second"

    registry = HopscotchRegistry()
    scan(registry, locals_dict=locals())

    component_types = list(registry.get_by_category("component"))
    assert FirstComponent in component_types
    assert SecondComponent in component_types


def test_list_middlewares_works_with_categories():
    """Verify list_middlewares() introspection works with category system."""
    from tdom_svcs import list_middlewares

    @middleware
    @dataclass
    class IntrospectionMiddleware:
        priority: int = 5

        def __call__(self, component, props, context):
            return props

    registry = HopscotchRegistry()
    scan(registry, locals_dict=locals())

    middlewares = list_middlewares(registry)
    names = [m.middleware_type.__name__ for m in middlewares]
    assert "IntrospectionMiddleware" in names


def test_get_components_by_category():
    """Verify registry.get_by_category() works for components."""

    @component
    @dataclass
    class IntrospectionComponent:
        value: str = "test"

    registry = HopscotchRegistry()
    scan(registry, locals_dict=locals())

    # Components should be retrievable via category
    components = list(registry.get_by_category("component"))
    assert IntrospectionComponent in components
