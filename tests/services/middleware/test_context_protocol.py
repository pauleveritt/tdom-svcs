"""
Tests for Context Protocol.

This module tests the Context protocol which defines a dict-like interface
for accessing dependencies and state in middleware.
"""

from typing import Any

import pytest
import svcs

from tdom_svcs.services.middleware import Context


# Test fixtures - custom context implementations


class CustomContext:
    """Custom dict-like context implementation."""

    def __init__(self, data: dict[str, Any]):
        self._data = data

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)


class SvcsContainerWrapper:
    """
    Wrapper around svcs.Container to provide dict-like interface.

    This wrapper makes svcs.Container satisfy the Context protocol by
    providing both __getitem__ and get() methods.
    """

    def __init__(self, container: svcs.Container):
        self._container = container

    def __getitem__(self, key: Any) -> Any:
        return self._container.get(key)

    def get(self, key: Any, default: Any = None) -> Any:
        try:
            return self._container.get(key)
        except LookupError:
            return default


def test_protocol_satisfaction_with_plain_dict():
    """Test that plain dict satisfies Context protocol."""
    context = {"logger": "test_logger", "config": {"debug": True}}

    # Check protocol satisfaction
    assert isinstance(context, Context)


def test_protocol_satisfaction_with_wrapped_container():
    """Test that wrapped svcs.Container satisfies Context protocol."""
    registry = svcs.Registry()
    container = svcs.Container(registry)
    wrapped = SvcsContainerWrapper(container)

    # Wrapped container satisfies Context protocol
    assert isinstance(wrapped, Context)


def test_protocol_satisfaction_with_custom_implementation():
    """Test that custom dict-like objects satisfy Context protocol."""
    context = CustomContext({"logger": "test_logger"})

    assert isinstance(context, Context)


def test_dict_getitem_access():
    """Test __getitem__ access with plain dict."""
    context = {"logger": "test_logger", "db": "db_connection"}

    # Access items via bracket notation
    assert context["logger"] == "test_logger"
    assert context["db"] == "db_connection"


def test_dict_getitem_missing_key():
    """Test __getitem__ raises KeyError for missing keys."""
    context = {"logger": "test_logger"}

    with pytest.raises(KeyError):
        _ = context["missing_key"]


def test_dict_get_access():
    """Test get() method with plain dict."""
    context = {"logger": "test_logger"}

    # get() with existing key
    assert context.get("logger") == "test_logger"

    # get() with missing key returns None
    assert context.get("missing_key") is None

    # get() with default value
    assert context.get("missing_key", "default") == "default"


def test_wrapped_container_getitem_access():
    """Test __getitem__ access with wrapped svcs.Container."""
    registry = svcs.Registry()
    container = svcs.Container(registry)
    wrapped = SvcsContainerWrapper(container)

    # Register a value
    registry.register_value(str, "test_value", enter=False)

    # Access via __getitem__ (using type keys like svcs)
    result = wrapped[str]
    assert result == "test_value"


def test_wrapped_container_get_access():
    """Test get() method with wrapped svcs.Container."""
    registry = svcs.Registry()
    container = svcs.Container(registry)
    wrapped = SvcsContainerWrapper(container)

    # Register a value
    registry.register_value(str, "test_value", enter=False)

    # Access via get() with type key
    result = wrapped.get(str)
    assert result == "test_value"


def test_custom_context_getitem():
    """Test __getitem__ with custom context implementation."""
    context = CustomContext({"logger": "test_logger", "config": {"debug": True}})

    assert context["logger"] == "test_logger"
    assert context["config"]["debug"] is True


def test_custom_context_get():
    """Test get() with custom context implementation."""
    context = CustomContext({"logger": "test_logger"})

    assert context.get("logger") == "test_logger"
    assert context.get("missing", "default") == "default"
