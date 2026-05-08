"""
Tests for the html() wrapper function in tdom_svcs.

These tests verify that html() accepts an optional container parameter,
delegates correctly when container=None, and manages TemplateProcessor
lifecycle via the container.
"""

# White-box test import: compares html() output against tdom.html() directly.
# Not a user-facing example — public code uses `from tdom_svcs import html`.
import tdom
from svcs_hopscotch.injectors import HopscotchContainer, HopscotchRegistry
from tdom.processor import TemplateProcessor

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


def test_html_no_container_delegates_to_tdom():
    """html() with no container must produce byte-identical output to tdom.html()."""
    template = t"<div><p>Hello</p></div>"
    assert html(template) == tdom.html(template)


def test_html_no_container_void_elements():
    """html() without container uses slash_void=True (same as tdom default)."""
    result = html(t"<br />")
    assert result == "<br />"


def test_html_container_lazy_registers_template_processor():
    """First html() call on a container lazily registers TemplateProcessor."""
    registry = HopscotchRegistry()
    with HopscotchContainer(registry) as container:
        assert not _has_template_processor(container)
        html(t"<div>test</div>", container=container)
        assert _has_template_processor(container)


def test_html_container_reuses_registered_processor():
    """Subsequent html() calls on same container reuse the registered TemplateProcessor."""
    registry = HopscotchRegistry()
    with HopscotchContainer(registry) as container:
        html(t"<div>first</div>", container=container)
        tp_first = container.get(TemplateProcessor)
        html(t"<div>second</div>", container=container)
        tp_second = container.get(TemplateProcessor)
        assert tp_first is tp_second


def test_html_different_containers_get_separate_processors():
    """Each container gets its own TemplateProcessor instance."""
    registry = HopscotchRegistry()
    with HopscotchContainer(registry) as c1, HopscotchContainer(registry) as c2:
        html(t"<div>a</div>", container=c1)
        html(t"<div>b</div>", container=c2)
        assert c1.get(TemplateProcessor) is not c2.get(TemplateProcessor)


def _has_template_processor(container: HopscotchContainer) -> bool:
    """Helper: check whether TemplateProcessor is registered on the container."""
    import svcs.exceptions

    try:
        container.get(TemplateProcessor)
        return True
    except svcs.exceptions.ServiceNotFoundError:
        return False
