"""Tests for additional categories support in middleware and component decorators."""

from dataclasses import dataclass

from svcs_di.injectors import HopscotchRegistry

from tdom_svcs import component, middleware, register_middleware, scan
from tdom_svcs.services.middleware import register_component


def test_middleware_decorator_with_additional_categories():
    """Test @middleware decorator accepts and merges additional categories."""

    @middleware(categories=["security", "auth"])
    @dataclass
    class AuthMiddleware:
        priority: int = 0

        def __call__(self, component, props, context):
            return props

    # Check that it has all categories
    assert hasattr(AuthMiddleware, "__injectable_metadata__")
    metadata = AuthMiddleware.__injectable_metadata__
    categories = metadata["categories"]

    assert "middleware" in categories
    assert "security" in categories
    assert "auth" in categories
    assert len(categories) == 3


def test_middleware_decorator_without_additional_categories():
    """Test @middleware decorator works without additional categories."""

    @middleware
    @dataclass
    class BasicMiddleware:
        priority: int = 0

        def __call__(self, component, props, context):
            return props

    metadata = BasicMiddleware.__injectable_metadata__
    categories = metadata["categories"]

    assert categories == ("middleware",)


def test_middleware_can_be_found_by_all_categories():
    """Test middleware can be retrieved by any of its categories."""

    @middleware(categories=["security", "logging"])
    @dataclass
    class SecurityLogger:
        priority: int = 0

        def __call__(self, component, props, context):
            return props

    registry = HopscotchRegistry()
    scan(registry, locals_dict=locals())

    # Should be findable by all categories
    assert SecurityLogger in registry.get_by_category("middleware")
    assert SecurityLogger in registry.get_by_category("security")
    assert SecurityLogger in registry.get_by_category("logging")


def test_register_middleware_with_additional_categories():
    """Test imperative register_middleware with additional categories."""

    @dataclass
    class ImperativeMiddleware:
        priority: int = 0

        def __call__(self, component, props, context):
            return props

    registry = HopscotchRegistry()
    register_middleware(registry, ImperativeMiddleware, categories=["security", "audit"])

    # Should be in all categories
    assert ImperativeMiddleware in registry.get_by_category("middleware")
    assert ImperativeMiddleware in registry.get_by_category("security")
    assert ImperativeMiddleware in registry.get_by_category("audit")


def test_register_middleware_without_additional_categories():
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


def test_component_decorator_with_additional_categories():
    """Test @component decorator accepts and merges additional categories."""

    @component(categories=["page", "admin"])
    @dataclass
    class AdminPage:
        title: str = "Admin"

    # Check that it has all categories
    assert hasattr(AdminPage, "__injectable_metadata__")
    metadata = AdminPage.__injectable_metadata__
    categories = metadata["categories"]

    assert "component" in categories
    assert "page" in categories
    assert "admin" in categories
    assert len(categories) == 3


def test_component_decorator_without_additional_categories():
    """Test @component decorator works without additional categories."""

    @component
    @dataclass
    class BasicComponent:
        value: str = "test"

    metadata = BasicComponent.__injectable_metadata__
    categories = metadata["categories"]

    assert categories == ("component",)


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

    # Check categories
    metadata = DashboardPage.__injectable_metadata__
    categories = metadata["categories"]

    assert "component" in categories
    assert "page" in categories
    assert "dashboard" in categories

    # Check middleware config
    from tdom_svcs.services.middleware.decorators import COMPONENT_MIDDLEWARE_ATTR

    mw_config = getattr(DashboardPage, COMPONENT_MIDDLEWARE_ATTR)
    assert "pre_resolution" in mw_config
    assert TestMiddleware in mw_config["pre_resolution"]


def test_component_can_be_found_by_all_categories():
    """Test component can be retrieved by any of its categories."""

    @component(categories=["widget", "interactive"])
    @dataclass
    class Button:
        label: str = "Click"

    registry = HopscotchRegistry()
    scan(registry, locals_dict=locals())

    # Should be findable by all categories
    assert Button in registry.get_by_category("component")
    assert Button in registry.get_by_category("widget")
    assert Button in registry.get_by_category("interactive")


def test_register_component_with_additional_categories():
    """Test imperative register_component with additional categories."""

    @dataclass
    class ImperativeComponent:
        value: str = "test"

    registry = HopscotchRegistry()
    register_component(registry, ImperativeComponent, categories=["page", "settings"])

    # Should be in all categories
    assert ImperativeComponent in registry.get_by_category("component")
    assert ImperativeComponent in registry.get_by_category("page")
    assert ImperativeComponent in registry.get_by_category("settings")


def test_register_component_without_additional_categories():
    """Test imperative register_component without additional categories."""

    @dataclass
    class SimpleComponent:
        value: str = "test"

    registry = HopscotchRegistry()
    register_component(registry, SimpleComponent)

    assert SimpleComponent in registry.get_by_category("component")
    categories = registry.get_categories(SimpleComponent)
    assert categories == frozenset(["component"])


def test_multiple_items_with_same_additional_category():
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

    # Both middleware should be in "security" category
    security_items = list(registry.get_by_category("security"))
    assert AuthMiddleware in security_items
    assert ValidationMiddleware in security_items
    assert len(security_items) == 2

    # Component should be in "secure" category
    assert SecureComponent in registry.get_by_category("secure")


def test_list_all_categories_includes_additional():
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
