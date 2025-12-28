"""
Tests for the html() wrapper function in tdom_svcs.

These tests verify that html() accepts optional config and context parameters
while maintaining backward compatibility.
"""

import typing
from collections.abc import Mapping
from dataclasses import dataclass

import pytest

from tdom_svcs import ComponentLookup, Config, html


def test_html_without_parameters():
    """Test that html() works without config and context parameters (backward compatibility)."""
    node = html(t"<div>Hello</div>")
    assert str(node) == "<div>Hello</div>"

    # Also test with more complex template
    name = "World"
    node = html(t"<p>Hello, {name}!</p>")
    assert str(node) == "<p>Hello, World!</p>"


def test_html_accepts_config_parameter():
    """Test that html() accepts config parameter."""

    @dataclass
    class MockConfig:
        component_lookup: ComponentLookup | None = None

    mock_config = MockConfig(component_lookup=None)

    # Should accept config without error
    node = html(t"<div>Hello</div>", config=mock_config)
    assert str(node) == "<div>Hello</div>"


def test_html_accepts_context_parameter():
    """Test that html() accepts context parameter."""
    mock_context: Mapping[str, typing.Any] = {"key": "value"}

    # Should accept context without error
    node = html(t"<div>Hello</div>", context=mock_context)
    assert str(node) == "<div>Hello</div>"


def test_html_accepts_both_config_and_context():
    """Test that html() accepts both config and context parameters."""

    @dataclass
    class MockConfig:
        component_lookup: ComponentLookup | None = None

    mock_config = MockConfig(component_lookup=None)
    mock_context: Mapping[str, typing.Any] = {"key": "value"}

    # Should accept both parameters without error
    node = html(t"<div>Hello</div>", config=mock_config, context=mock_context)
    assert str(node) == "<div>Hello</div>"


def test_html_with_explicit_none():
    """Test that html() accepts explicit None for config and context."""
    node = html(t"<div>Test</div>", config=None, context=None)
    assert str(node) == "<div>Test</div>"


def test_html_with_nested_elements():
    """Test that html() works with nested elements."""

    @dataclass
    class MockConfig:
        component_lookup: ComponentLookup | None = None

    mock_config = MockConfig(component_lookup=None)
    mock_context: Mapping[str, typing.Any] = {"key": "value"}

    # Nested elements should process without error
    node = html(
        t"<div><p>Nested</p><span>Content</span></div>",
        config=mock_config,
        context=mock_context,
    )
    assert str(node) == "<div><p>Nested</p><span>Content</span></div>"
