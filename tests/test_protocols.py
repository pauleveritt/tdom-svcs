"""
Tests for Protocol definitions in tdom_svcs.

These tests verify that the Config and ComponentLookup protocols work correctly
with runtime_checkable behavior and accept duck-typed implementations.
"""

import typing
from collections.abc import Mapping
from dataclasses import dataclass

import pytest

from tdom_svcs import ComponentLookup, Config


# Create runtime_checkable versions for testing
@typing.runtime_checkable
class RuntimeComponentLookup(ComponentLookup, typing.Protocol):
    """Runtime checkable version of ComponentLookup for testing."""
    pass


@typing.runtime_checkable
class RuntimeConfig(Config, typing.Protocol):
    """Runtime checkable version of Config for testing."""
    pass


def test_component_lookup_protocol_accepts_duck_typed_class():
    """Test that ComponentLookup protocol accepts implementations without inheritance."""

    @dataclass
    class MockComponentLookup:
        """Mock implementation that satisfies ComponentLookup protocol."""

        container: object

        def __call__(self, name: str, context: Mapping[str, typing.Any]) -> typing.Callable | None:
            # Simple mock: return None (component not found)
            return None

    # Create an instance and verify it satisfies the protocol
    mock_lookup = MockComponentLookup(container="some_container")
    assert isinstance(mock_lookup, RuntimeComponentLookup)

    # Verify we can call it
    result = mock_lookup("Button", {"key": "value"})
    assert result is None


def test_component_lookup_protocol_can_return_callable():
    """Test that ComponentLookup can return a callable component."""

    def sample_component(*, children: tuple = ()) -> str:
        return f"<div>Component with {len(children)} children</div>"

    @dataclass
    class MockComponentLookup:
        """Mock implementation that returns a component."""

        container: object

        def __call__(self, name: str, context: Mapping[str, typing.Any]) -> typing.Callable | None:
            if name == "Button":
                return sample_component
            return None

    mock_lookup = MockComponentLookup(container="some_container")
    assert isinstance(mock_lookup, RuntimeComponentLookup)

    # Verify it returns the component
    result = mock_lookup("Button", {})
    assert result is sample_component
    assert callable(result)


def test_config_protocol_accepts_duck_typed_class():
    """Test that Config protocol accepts implementations without inheritance."""

    @dataclass
    class MockConfig:
        """Mock implementation that satisfies Config protocol."""

        component_lookup: ComponentLookup | None = None

    # Create an instance and verify it satisfies the protocol
    mock_config = MockConfig(component_lookup=None)
    assert isinstance(mock_config, RuntimeConfig)

    # Verify attribute access
    assert mock_config.component_lookup is None


def test_config_protocol_with_component_lookup():
    """Test that Config protocol works with ComponentLookup instance."""

    @dataclass
    class MockComponentLookup:
        container: object

        def __call__(self, name: str, context: Mapping[str, typing.Any]) -> typing.Callable | None:
            return None

    @dataclass
    class MockConfig:
        component_lookup: ComponentLookup | None = None

    mock_lookup = MockComponentLookup(container="some_container")
    mock_config = MockConfig(component_lookup=mock_lookup)

    assert isinstance(mock_config, RuntimeConfig)
    assert isinstance(mock_config.component_lookup, RuntimeComponentLookup)
