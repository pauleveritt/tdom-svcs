"""
Tests for the html() wrapper function in tdom_svcs.

These tests verify that html() accepts an optional context parameter
and returns correct HTML strings.
"""

from tdom_svcs import html


def test_html_basic():
    """Test html() renders templates without a container."""
    node = html(t"<div>Hello</div>")
    assert str(node) == "<div>Hello</div>"


def test_html_nested_elements():
    """Test html() with nested elements."""
    node = html(t"<div><p>Nested</p><span>Content</span></div>")
    assert str(node) == "<div><p>Nested</p><span>Content</span></div>"


def test_html_with_interpolation():
    """Test that html() works with template interpolation."""
    name = "World"
    node = html(t"<p>Hello, {name}!</p>")
    assert str(node) == "<p>Hello, World!</p>"
