"""Dependency injection processor for tdom templates.

NOTE: This module is a minimal stub for workspace compatibility (roadmap item 18).
The full DI-aware html() implementation that works with tstring-html v0.1.15+
will be written in roadmap item 20 ("Migrate Processor Off the Node-Based API").

The old node-object API (tdom.nodes.Node/Element/Fragment/Text) was removed in
tstring-html v0.1.15. This stub delegates to tdom.html() for all calls while
retaining the DI helper functions.
"""

from string.templatelib import Template

from markupsafe import Markup
from svcs_di.auto import get_field_infos
from tdom import html as tdom_html

from tdom_svcs.types import is_di_container

# --------------------------------------------------------------------------
# Type Aliases
# --------------------------------------------------------------------------

type ContextArg = object | None
type ConfigArg = object | None


# --------------------------------------------------------------------------
# DI Helper Functions
# --------------------------------------------------------------------------


def needs_dependency_injection(value: object) -> bool:
    """
    Check if a callable needs dependency injection.

    Uses svcs-di's get_field_infos() which handles both classes and functions.

    Args:
        value: The callable to check

    Returns:
        True if the callable has Inject[] or Resource[] fields/parameters, False otherwise
    """
    if not callable(value):
        return False
    field_infos = get_field_infos(value)
    return any(info.is_injectable or info.is_resource for info in field_infos)


# --------------------------------------------------------------------------
# _get_implementation — pure container/locator logic, no Node dependency
# --------------------------------------------------------------------------


def _get_implementation(context: ContextArg, cls: type) -> type:
    """
    Get the registered implementation for a class from the container's locator.

    Args:
        context: The context (potentially a DI container)
        cls: The class to look up an implementation for

    Returns:
        The registered implementation, or the original class if none found
    """
    if not is_di_container(context):
        return cls

    registry = getattr(context, "registry", None)
    if registry is None:
        return cls

    locator = getattr(registry, "locator", None)
    if locator is None:
        return cls

    get_impl = getattr(locator, "get_implementation", None)
    if get_impl is None:
        return cls

    resource = getattr(context, "resource", None)
    resource_type = type(resource) if resource is not None else None
    location = getattr(context, "location", None)

    impl = get_impl(cls, resource=resource_type, location=location)
    return impl if impl is not None else cls


# --------------------------------------------------------------------------
# html() — Minimal stub until item 20 rewrites this for tstring-html v0.1.15+
# --------------------------------------------------------------------------


def html(
    template: Template,
    *,
    config: ConfigArg = None,
    context: ContextArg = None,
) -> str | Markup:
    """
    Process a template string into an HTML string.

    Currently delegates to tdom.html() for all cases. The DI-aware path
    (context threading, component injection) will be implemented in
    roadmap item 20 when the processor is rewritten for the new
    ProcessorService API.

    Args:
        template: A template string created with the t"" literal
        config: Optional config object (accepted but currently unused)
        context: Optional context for dependency injection (accepted but unused)

    Returns:
        HTML string

    Examples:
        Basic usage:
        >>> node = html(t"<div>Hello</div>")
    """
    # config/context accepted for API compatibility; DI threading is item 20
    _ = config, context
    return tdom_html(template)
