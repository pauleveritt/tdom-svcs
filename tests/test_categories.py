"""Integration tests for kind and category support in middleware decorators."""

from dataclasses import dataclass
from typing import Any

from svcs_hopscotch.injectors import HopscotchRegistry

from tdom_svcs import (
    HOOKABLE_MIDDLEWARE_ATTR,
    Middleware,
    Props,
    PropsResult,
    Target,
    hookable,
    middleware,
    register_hookable,
    register_middleware,
    scan,
)


def test_middleware_sets_kind_metadata():
    """Verify @middleware re-export sets kind in injectable metadata."""

    @middleware
    @dataclass
    class MyMiddleware:
        priority: int = 0

        def __call__(self, target: Target, props: Props, context: Any) -> PropsResult:
            return props

    assert hasattr(MyMiddleware, "__injectable_metadata__")
    metadata = MyMiddleware.__injectable_metadata__
    assert metadata["kind"] == "middleware"
    assert metadata["categories"] is None


def test_middleware_with_additional_categories():
    """Test @middleware keeps additional categories as user facets."""

    @middleware(categories=["security", "auth"])
    @dataclass
    class AuthMiddleware:
        priority: int = 0

        def __call__(self, target, props, context):
            return props

    metadata = AuthMiddleware.__injectable_metadata__  # ty: ignore[unresolved-attribute]

    assert metadata["kind"] == "middleware"
    assert metadata["categories"] == ("security", "auth")


def test_hookable_sets_kind_and_middleware_attr():
    """Verify @hookable sets kind and middleware attribute when middleware is provided."""

    @middleware
    @dataclass
    class TestMiddleware:
        priority: int = 0

        def __call__(self, target, props, context):
            return props

    @hookable(middleware={"pre_resolution": [TestMiddleware]})
    @dataclass
    class MyHookable:
        value: str = "test"

    assert hasattr(MyHookable, "__injectable_metadata__")
    metadata = MyHookable.__injectable_metadata__
    assert metadata["kind"] == "hookable"
    assert metadata["categories"] is None

    assert hasattr(MyHookable, HOOKABLE_MIDDLEWARE_ATTR)
    mw_map = getattr(MyHookable, HOOKABLE_MIDDLEWARE_ATTR)
    assert "pre_resolution" in mw_map
    assert TestMiddleware in mw_map["pre_resolution"]


def test_middleware_found_by_kind_and_user_categories():
    """Test scan() discovers middleware by kind and user categories."""

    @middleware(categories=["security", "logging"])
    @dataclass
    class SecurityLogger:
        priority: int = 0

        def __call__(self, target, props, context):
            return props

    registry = HopscotchRegistry()
    scan(registry, locals_dict=locals())

    assert SecurityLogger in registry.get_by_kind("middleware")
    assert SecurityLogger not in registry.get_by_category("middleware")
    assert SecurityLogger in registry.get_by_category("security")
    assert SecurityLogger in registry.get_by_category("logging")


def test_hookable_found_by_kind_and_user_categories():
    """Test scan() discovers hookable items by kind and user categories."""

    @hookable(categories=["widget", "interactive"])
    @dataclass
    class Button:
        label: str = "Click"

    registry = HopscotchRegistry()
    scan(registry, locals_dict=locals())

    assert Button in registry.get_by_kind("hookable")
    assert Button not in registry.get_by_category("hookable")
    assert Button in registry.get_by_category("widget")
    assert Button in registry.get_by_category("interactive")


def test_list_middlewares_with_categories():
    """Verify list_middlewares() introspection works through re-exports."""
    from tdom_svcs import list_middlewares

    @middleware
    @dataclass
    class IntrospectionMiddleware:
        priority: int = 5

        def __call__(self, target, props, context):
            return props

    registry = HopscotchRegistry()
    scan(registry, locals_dict=locals())

    middlewares = list_middlewares(registry)
    names = [m.middleware_type.__name__ for m in middlewares]
    assert "IntrospectionMiddleware" in names


def test_register_middleware_with_categories():
    """Test register_middleware() stores kind and user categories."""

    @dataclass
    class ImperativeMiddleware(Middleware):
        priority: int = 0

        def __call__(self, target: Target, props: Props, context: Any) -> PropsResult:
            return props

    registry = HopscotchRegistry()
    register_middleware(
        registry, ImperativeMiddleware, categories=["security", "audit"]
    )

    assert ImperativeMiddleware in registry.get_by_kind("middleware")
    assert ImperativeMiddleware not in registry.get_by_category("middleware")
    assert ImperativeMiddleware in registry.get_by_category("security")
    assert ImperativeMiddleware in registry.get_by_category("audit")


def test_register_hookable_with_categories():
    """Test register_hookable() stores kind and user categories."""

    @dataclass
    class ImperativeHookable:
        value: str = "test"

    registry = HopscotchRegistry()
    register_hookable(registry, ImperativeHookable, categories=["page", "settings"])

    assert ImperativeHookable in registry.get_by_kind("hookable")
    assert ImperativeHookable not in registry.get_by_category("hookable")
    assert ImperativeHookable in registry.get_by_category("page")
    assert ImperativeHookable in registry.get_by_category("settings")
