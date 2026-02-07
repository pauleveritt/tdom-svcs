"""Tests for categories support in middleware and component decorators."""

from dataclasses import dataclass

from svcs_di.injectors import HopscotchRegistry

from tdom_svcs import component, middleware, register_middleware, scan
from tdom_svcs.services.middleware import register_component
from tdom_svcs.services.middleware.decorators import COMPONENT_MIDDLEWARE_ATTR


# --- Middleware decorator tests ---


def test_middleware_sets_category_metadata():
    """Verify @middleware sets categories in injectable metadata."""

    @middleware
    @dataclass
    class MyMiddleware:
        priority: int = 0

        def __call__(self, component, props, context):
            return props

    assert hasattr(MyMiddleware, "__injectable_metadata__")
    metadata = MyMiddleware.__injectable_metadata__
    assert "middleware" in metadata["categories"]
    assert metadata["categories"] == ("middleware",)


def test_middleware_with_additional_categories():
    """Test @middleware decorator accepts and merges additional categories."""

    @middleware(categories=["security", "auth"])
    @dataclass
    class AuthMiddleware:
        priority: int = 0

        def __call__(self, component, props, context):
            return props

    metadata = AuthMiddleware.__injectable_metadata__  # ty: ignore[unresolved-attribute]
    categories = metadata["categories"]

    assert "middleware" in categories
    assert "security" in categories
    assert "auth" in categories
    assert len(categories) == 3


def test_middleware_found_by_all_categories():
    """Test middleware can be retrieved by any of its categories."""

    @middleware(categories=["security", "logging"])
    @dataclass
    class SecurityLogger:
        priority: int = 0

        def __call__(self, component, props, context):
            return props

    registry = HopscotchRegistry()
    scan(registry, locals_dict=locals())

    assert SecurityLogger in registry.get_by_category("middleware")
    assert SecurityLogger in registry.get_by_category("security")
    assert SecurityLogger in registry.get_by_category("logging")


# --- Component decorator tests ---


def test_component_sets_category_and_middleware_attr():
    """Verify @component sets categories AND middleware attribute."""

    @component
    @dataclass
    class MyComponent:
        value: str = "test"

    assert hasattr(MyComponent, "__injectable_metadata__")
    metadata = MyComponent.__injectable_metadata__
    assert "component" in metadata["categories"]
    assert metadata["categories"] == ("component",)

    assert hasattr(MyComponent, COMPONENT_MIDDLEWARE_ATTR)
    assert getattr(MyComponent, COMPONENT_MIDDLEWARE_ATTR) == {}


def test_component_with_additional_categories():
    """Test @component decorator accepts and merges additional categories."""

    @component(categories=["page", "admin"])
    @dataclass
    class AdminPage:
        title: str = "Admin"

    metadata = AdminPage.__injectable_metadata__  # ty: ignore[unresolved-attribute]
    categories = metadata["categories"]

    assert "component" in categories
    assert "page" in categories
    assert "admin" in categories
    assert len(categories) == 3


def test_component_with_middleware_config():
    """Verify @component(middleware={...}) stores middleware config."""

    @middleware
    @dataclass
    class SampleMiddleware:
        priority: int = 0

        def __call__(self, component, props, context):
            return props

    @component(middleware={"pre_resolution": [SampleMiddleware]})
    @dataclass
    class MyComponent:
        value: str = "test"

    assert hasattr(MyComponent, "__injectable_metadata__")
    metadata = MyComponent.__injectable_metadata__
    assert "component" in metadata["categories"]

    mw_config = getattr(MyComponent, COMPONENT_MIDDLEWARE_ATTR)
    assert "pre_resolution" in mw_config
    assert SampleMiddleware in mw_config["pre_resolution"]


def test_component_with_middleware_and_categories():
    """Test @component with both middleware and categories parameters."""

    @middleware
    @dataclass
    class TestMiddleware:
        priority: int = 0

        def __call__(self, component, props, context):
            return props

    @component(
        middleware={"pre_resolution": [TestMiddleware]},
        categories=["page", "dashboard"],
    )
    @dataclass
    class DashboardPage:
        title: str = "Dashboard"

    metadata = DashboardPage.__injectable_metadata__  # ty: ignore[unresolved-attribute]
    categories = metadata["categories"]

    assert "component" in categories
    assert "page" in categories
    assert "dashboard" in categories

    mw_config = getattr(DashboardPage, COMPONENT_MIDDLEWARE_ATTR)
    assert "pre_resolution" in mw_config
    assert TestMiddleware in mw_config["pre_resolution"]


def test_component_found_by_all_categories():
    """Test component can be retrieved by any of its categories."""

    @component(categories=["widget", "interactive"])
    @dataclass
    class Button:
        label: str = "Click"

    registry = HopscotchRegistry()
    scan(registry, locals_dict=locals())

    assert Button in registry.get_by_category("component")
    assert Button in registry.get_by_category("widget")
    assert Button in registry.get_by_category("interactive")


# --- Imperative registration tests ---


def test_register_middleware_with_categories():
    """Test imperative register_middleware with additional categories."""

    @dataclass
    class ImperativeMiddleware:
        priority: int = 0

        def __call__(self, component, props, context):
            return props

    registry = HopscotchRegistry()
    register_middleware(
        registry, ImperativeMiddleware, categories=["security", "audit"]
    )

    assert ImperativeMiddleware in registry.get_by_category("middleware")
    assert ImperativeMiddleware in registry.get_by_category("security")
    assert ImperativeMiddleware in registry.get_by_category("audit")


def test_register_middleware_without_categories():
    """Test imperative register_middleware without additional categories."""

    @dataclass
    class SimpleMiddleware:
        priority: int = 0

        def __call__(self, component, props, context):
            return props

    registry = HopscotchRegistry()
    register_middleware(registry, SimpleMiddleware)

    assert SimpleMiddleware in registry.get_by_category("middleware")
    categories = registry.get_categories(SimpleMiddleware)
    assert categories == frozenset(["middleware"])


def test_register_component_with_categories():
    """Test imperative register_component with additional categories."""

    @dataclass
    class ImperativeComponent:
        value: str = "test"

    registry = HopscotchRegistry()
    register_component(registry, ImperativeComponent, categories=["page", "settings"])

    assert ImperativeComponent in registry.get_by_category("component")
    assert ImperativeComponent in registry.get_by_category("page")
    assert ImperativeComponent in registry.get_by_category("settings")


def test_register_component_without_categories():
    """Test imperative register_component without additional categories."""

    @dataclass
    class SimpleComponent:
        value: str = "test"

    registry = HopscotchRegistry()
    register_component(registry, SimpleComponent)

    assert SimpleComponent in registry.get_by_category("component")
    categories = registry.get_categories(SimpleComponent)
    assert categories == frozenset(["component"])


# --- Scanning tests ---


def test_scan_discovers_middleware_by_category():
    """Verify scan() discovers middleware via categories."""

    @middleware
    @dataclass
    class ScanMiddleware:
        priority: int = 0

        def __call__(self, component, props, context):
            return props

    registry = HopscotchRegistry()
    scan(registry, locals_dict=locals())

    middleware_types = list(registry.get_by_category("middleware"))
    assert ScanMiddleware in middleware_types


def test_scan_discovers_components_by_category():
    """Verify scan() discovers components via categories."""

    @component
    @dataclass
    class ScanComponent:
        value: str = "test"

    registry = HopscotchRegistry()
    scan(registry, locals_dict=locals())

    component_types = list(registry.get_by_category("component"))
    assert ScanComponent in component_types


def test_scan_multiple_middleware():
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


def test_scan_multiple_components():
    """Verify multiple components can be discovered in single scan."""

    @middleware
    @dataclass
    class MwForComponent:
        priority: int = 0

        def __call__(self, component, props, context):
            return props

    @component
    @dataclass
    class FirstComponent:
        value: str = "first"

    @component(middleware={"pre_resolution": [MwForComponent]})
    @dataclass
    class SecondComponent:
        value: str = "second"

    registry = HopscotchRegistry()
    scan(registry, locals_dict=locals())

    component_types = list(registry.get_by_category("component"))
    assert FirstComponent in component_types
    assert SecondComponent in component_types


def test_multiple_items_same_category():
    """Test multiple middleware/components can share additional categories."""

    @middleware(categories=["security"])
    @dataclass
    class AuthMiddleware:
        priority: int = 0

        def __call__(self, component, props, context):
            return props

    @middleware(categories=["security"])
    @dataclass
    class ValidationMiddleware:
        priority: int = 10

        def __call__(self, component, props, context):
            return props

    @component(categories=["secure"])
    @dataclass
    class SecureComponent:
        value: str = "test"

    registry = HopscotchRegistry()
    scan(registry, locals_dict=locals())

    security_items = list(registry.get_by_category("security"))
    assert AuthMiddleware in security_items
    assert ValidationMiddleware in security_items
    assert len(security_items) == 2

    assert SecureComponent in registry.get_by_category("secure")


# --- Introspection tests ---


def test_list_middlewares_with_categories():
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


def test_list_categories_includes_additional():
    """Test that list_categories() includes additional categories."""

    @middleware(categories=["custom1"])
    @dataclass
    class Middleware1:
        priority: int = 0

        def __call__(self, component, props, context):
            return props

    @component(categories=["custom2"])
    @dataclass
    class Component1:
        value: str = "test"

    registry = HopscotchRegistry()
    scan(registry, locals_dict=locals())

    all_categories = registry.list_categories()
    assert "middleware" in all_categories
    assert "component" in all_categories
    assert "custom1" in all_categories
    assert "custom2" in all_categories
