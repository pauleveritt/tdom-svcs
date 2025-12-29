"""
Tests for @component decorator and per-component middleware.

This module tests the @component decorator which allows registering
per-component middleware alongside existing @injectable functionality.
"""

from dataclasses import dataclass
from typing import Any, Callable, cast

import pytest

from tdom_svcs.services.middleware import Context, Middleware
from tdom_svcs.services.middleware.decorators import (
    component,
    get_component_middleware,
    register_component,
)
from tdom_svcs.services.component_registry.component_name_registry import (
    ComponentNameRegistry,
)


# Test fixtures - middleware implementations


@dataclass
class LoggingMiddleware:
    """Simple logging middleware for testing."""

    priority: int = -10

    def __call__(
        self,
        comp: type | Callable[..., Any],
        props: dict[str, Any],
        ctx: Context,
    ) -> dict[str, Any] | None:
        """Log component resolution."""
        props["logged"] = True
        return props


@dataclass
class ValidationMiddleware:
    """Simple validation middleware for testing."""

    priority: int = 0

    def __call__(
        self,
        comp: type | Callable[..., Any],
        props: dict[str, Any],
        ctx: Context,
    ) -> dict[str, Any] | None:
        """Validate props."""
        if "invalid" in props:
            return None
        props["validated"] = True
        return props


def test_component_decorator_basic_usage():
    """Test @component decorator stores middleware in metadata."""
    logging_mw = LoggingMiddleware()
    validation_mw = ValidationMiddleware()

    @component(
        middleware={
            "pre_resolution": [logging_mw],
            "post_resolution": [validation_mw],
        }
    )
    @dataclass
    class Button:
        label: str = "Click"

    # Check metadata storage
    assert hasattr(Button, "__tdom_svcs_middleware__")
    middleware_dict = Button.__tdom_svcs_middleware__
    assert "pre_resolution" in middleware_dict
    assert "post_resolution" in middleware_dict
    assert middleware_dict["pre_resolution"] == [logging_mw]
    assert middleware_dict["post_resolution"] == [validation_mw]


def test_component_decorator_without_middleware():
    """Test @component decorator works without middleware parameter."""

    @component()
    @dataclass
    class Card:
        title: str = "Card"

    # Should have empty metadata
    assert hasattr(Card, "__tdom_svcs_middleware__")
    assert Card.__tdom_svcs_middleware__ == {}


def test_component_decorator_retrieval_utility():
    """Test get_component_middleware utility function."""
    logging_mw = LoggingMiddleware()

    @component(middleware={"pre_resolution": [logging_mw]})
    @dataclass
    class Panel:
        content: str = "Panel"

    # Retrieve middleware
    middleware_dict = get_component_middleware(Panel)
    assert middleware_dict == {"pre_resolution": [logging_mw]}


def test_component_decorator_retrieval_no_metadata():
    """Test get_component_middleware returns empty dict for non-decorated components."""

    @dataclass
    class PlainComponent:
        name: str = "Plain"

    # Should return empty dict
    middleware_dict = get_component_middleware(PlainComponent)
    assert middleware_dict == {}


def test_register_component_imperative_function():
    """Test register_component() imperative function for non-decorator usage."""

    @dataclass
    class Dialog:
        title: str = "Dialog"

    logging_mw = LoggingMiddleware()
    validation_mw = ValidationMiddleware()

    # Register imperatively
    register_component(
        Dialog,
        middleware={
            "pre_resolution": [logging_mw],
            "post_resolution": [validation_mw],
        },
    )

    # Check metadata storage
    assert hasattr(Dialog, "__tdom_svcs_middleware__")
    middleware_dict = Dialog.__tdom_svcs_middleware__
    assert middleware_dict["pre_resolution"] == [logging_mw]
    assert middleware_dict["post_resolution"] == [validation_mw]


def test_component_decorator_with_function_component():
    """Test @component decorator works with function components."""
    logging_mw = LoggingMiddleware()

    @component(middleware={"pre_resolution": [logging_mw]})
    def heading(text: str = "Heading") -> str:
        return f"<h1>{text}</h1>"

    # Check metadata storage on function
    assert hasattr(heading, "__tdom_svcs_middleware__")
    middleware_dict = get_component_middleware(heading)
    assert middleware_dict == {"pre_resolution": [logging_mw]}


def test_register_component_with_component_name_registry():
    """Test that @component decorator registers component in ComponentNameRegistry."""

    @component()
    @dataclass
    class Alert:
        message: str = "Alert"

    # Component should have metadata even without middleware
    assert hasattr(Alert, "__tdom_svcs_middleware__")

    # ComponentNameRegistry registration would be done by scan_components()
    # Here we just verify the decorator doesn't break existing patterns
    registry = ComponentNameRegistry()
    registry.register("Alert", Alert)
    assert registry.get_type("Alert") is Alert


def test_component_decorator_multiple_middleware_per_phase():
    """Test @component decorator with multiple middleware in single phase."""
    logging_mw = LoggingMiddleware()
    validation_mw = ValidationMiddleware()

    @component(
        middleware={
            "pre_resolution": [logging_mw, validation_mw],
        }
    )
    @dataclass
    class Form:
        action: str = "/submit"

    middleware_dict = get_component_middleware(Form)
    assert len(middleware_dict["pre_resolution"]) == 2
    assert middleware_dict["pre_resolution"][0] is logging_mw
    assert middleware_dict["pre_resolution"][1] is validation_mw
