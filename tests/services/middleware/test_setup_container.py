"""
Tests for setup_container() utility function.

This module tests the setup_container() function which validates and optionally
registers context for middleware access.
"""

from typing import Any, cast

import pytest
import svcs
from svcs.exceptions import ServiceNotFoundError

from tdom_svcs.services.middleware import (
    Context,
    MiddlewareManager,
    setup_container,
)


class CustomContext:
    """Custom dict-like context implementation."""

    def __init__(self, data: dict[str, Any]):
        self._data = data

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)


def test_setup_container_with_plain_dict():
    """Test setup_container validates plain dict."""
    context = {"logger": "test_logger", "config": {"debug": True}}

    # Should not raise error
    setup_container(context)

    # Dict should satisfy Context protocol
    assert isinstance(context, Context)


def test_setup_container_with_svcs_registry():
    """Test setup_container registers context in svcs.Registry."""
    registry = svcs.Registry()
    context = {"logger": "test_logger", "config": {"debug": True}}

    # Setup with registry registers the context
    setup_container(context, registry)

    # Verify registration by creating a container and getting it back
    container = svcs.Container(registry)
    retrieved = container.get(Context)
    assert retrieved is context
    assert retrieved["logger"] == "test_logger"


def test_setup_container_with_custom_context():
    """Test setup_container accepts custom dict-like objects."""
    custom = CustomContext({"logger": "test_logger"})

    # Should not raise error
    setup_container(custom)

    # Custom context should satisfy protocol
    assert isinstance(custom, Context)


def test_setup_container_with_custom_context_and_registry():
    """Test setup_container registers custom context in registry."""
    registry = svcs.Registry()
    custom = CustomContext({"logger": "test_logger"})

    # Setup with registry
    setup_container(custom, registry)

    # Verify registration
    container = svcs.Container(registry)
    retrieved = container.get(Context)
    assert retrieved is custom
    assert retrieved["logger"] == "test_logger"


def test_setup_container_with_invalid_context():
    """Test setup_container raises TypeError for invalid context."""

    # Object that doesn't satisfy Context protocol
    class InvalidContext:
        pass

    invalid = InvalidContext()

    with pytest.raises(TypeError, match="does not satisfy Context protocol"):
        setup_container(invalid)  # type: ignore[arg-type]


def test_setup_container_with_invalid_registry():
    """Test setup_container raises TypeError for invalid registry."""
    context = {"logger": "test_logger"}

    # Object that doesn't have register_value
    class InvalidRegistry:
        pass

    invalid = InvalidRegistry()

    with pytest.raises(TypeError, match="does not have 'register_value' method"):
        setup_container(context, invalid)


def test_setup_container_registers_manager_as_service():
    """Test setup_container registers MiddlewareManager as a service by default."""
    registry = svcs.Registry()
    context = {"logger": "test_logger"}

    # Setup (manager registered by default)
    setup_container(context, registry)

    # Verify both Context and MiddlewareManager are registered
    container = svcs.Container(registry)

    # Context should be available
    retrieved_context = container.get(Context)
    assert retrieved_context is context

    # MiddlewareManager should be available as a service
    manager = container.get(MiddlewareManager)
    assert isinstance(manager, MiddlewareManager)


def test_setup_container_manager_registration_without_registry():
    """Test register_manager has no effect without registry."""
    context = {"logger": "test_logger"}

    # Should not raise error even with register_manager=True
    # (just ignores it when no registry provided)
    setup_container(context, register_manager=True)

    # Context should still satisfy protocol
    assert isinstance(context, Context)


def test_setup_container_manager_singleton_per_container():
    """Test MiddlewareManager is singleton within container scope."""
    registry = svcs.Registry()
    context = {"logger": "test_logger"}

    setup_container(context, registry)

    container = svcs.Container(registry)

    # Get manager twice from same container
    manager1 = container.get(MiddlewareManager)
    manager2 = container.get(MiddlewareManager)

    # Should be same instance within container
    assert manager1 is manager2


def test_setup_container_manager_with_invalid_registry():
    """Test register_manager with registry that lacks register_factory."""
    context = {"logger": "test_logger"}

    # Create a registry-like object with register_value but not register_factory
    class PartialRegistry:
        def register_value(self, *args, **kwargs):
            pass

    partial = PartialRegistry()

    with pytest.raises(TypeError, match="does not have 'register_factory' method"):
        setup_container(context, partial, register_manager=True)


def test_setup_container_skip_manager_registration():
    """Test register_manager=False skips MiddlewareManager registration."""
    registry = svcs.Registry()
    context = {"logger": "test_logger"}

    # Explicitly disable manager registration
    setup_container(context, registry, register_manager=False)

    container = svcs.Container(registry)

    # Context should be available
    retrieved_context = container.get(Context)
    assert retrieved_context is context

    # MiddlewareManager should NOT be available
    with pytest.raises(ServiceNotFoundError):
        container.get(MiddlewareManager)


def test_setup_container_manager_service_is_functional():
    """Test that registered MiddlewareManager service is fully functional."""
    registry = svcs.Registry()
    context = {"logger": "test_logger"}

    setup_container(context, registry)

    # Get manager from container
    container = svcs.Container(registry)
    manager = container.get(MiddlewareManager)

    # Test that manager works - register and execute middleware
    from dataclasses import dataclass

    @dataclass
    class TestMiddleware:
        priority: int = 0

        def __call__(self, component, props, context):
            props["tested"] = True
            return props

    manager.register_middleware(TestMiddleware())

    class TestComponent:
        pass

    props = {}
    result = manager.execute(TestComponent, props, cast(Context, context))

    assert result is not None
    assert result["tested"] is True
