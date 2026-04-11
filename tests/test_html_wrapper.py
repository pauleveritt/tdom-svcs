"""
Tests for the html() wrapper function in tdom_svcs.

These tests verify that html() accepts an optional context parameter
and returns correct HTML strings.
"""

import pytest

from tdom_svcs import html


@pytest.mark.parametrize(
    ("template", "expected", "context"),
    [
        # Basic usage without context
        (t"<div>Hello</div>", "<div>Hello</div>", None),
        # With dict context (no DI triggered)
        (t"<div>Hello</div>", "<div>Hello</div>", {"key": "value"}),
        # Nested elements
        (
            t"<div><p>Nested</p><span>Content</span></div>",
            "<div><p>Nested</p><span>Content</span></div>",
            {"key": "value"},
        ),
    ],
)
def test_html_with_context(template, expected, context):
    """Test html() with various context parameters."""
    if context is None:
        node = html(template)
    else:
        node = html(template, context=context)

    assert str(node) == expected


def test_html_with_interpolation():
    """Test that html() works with template interpolation."""
    name = "World"
    node = html(t"<p>Hello, {name}!</p>")
    assert str(node) == "<p>Hello, World!</p>"
