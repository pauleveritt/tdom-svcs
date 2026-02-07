"""
Tests for the html() wrapper function in tdom_svcs.

These tests verify that html() accepts optional config and context parameters
while maintaining backward compatibility.
"""

from dataclasses import dataclass

import pytest

from tdom_svcs import html


@dataclass
class MockConfig:
    """Mock config for testing."""

    pass


@pytest.mark.parametrize(
    ("template", "expected", "config", "context"),
    [
        # Basic backward compatibility
        (t"<div>Hello</div>", "<div>Hello</div>", None, None),
        # With config only
        (t"<div>Hello</div>", "<div>Hello</div>", MockConfig(), None),
        # With context only
        (t"<div>Hello</div>", "<div>Hello</div>", None, {"key": "value"}),
        # With both config and context
        (
            t"<div>Hello</div>",
            "<div>Hello</div>",
            MockConfig(),
            {"key": "value"},
        ),
        # Nested elements
        (
            t"<div><p>Nested</p><span>Content</span></div>",
            "<div><p>Nested</p><span>Content</span></div>",
            MockConfig(),
            {"key": "value"},
        ),
    ],
)
def test_html_with_config_and_context(template, expected, config, context):
    """Test html() with various combinations of config and context parameters."""
    if config is None and context is None:
        node = html(template)
    elif config is not None and context is None:
        node = html(template, config=config)
    elif config is None and context is not None:
        node = html(template, context=context)
    else:
        node = html(template, config=config, context=context)

    assert str(node) == expected


def test_html_with_interpolation():
    """Test that html() works with template interpolation."""
    name = "World"
    node = html(t"<p>Hello, {name}!</p>")
    assert str(node) == "<p>Hello, World!</p>"
