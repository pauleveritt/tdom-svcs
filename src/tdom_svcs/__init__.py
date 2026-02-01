"""tdom-svcs: Dependency injection for tdom templates."""

from tdom_svcs.middleware import (
    execute_middleware,
    execute_middleware_async,
    middleware,
    register_middleware,
)
from tdom_svcs.processor import html
from tdom_svcs.scanning import scan
from tdom_svcs.services.middleware.decorators import (
    component,
    execute_component_middleware,
    get_component_middleware,
)
from tdom_svcs.types import Component

# Note: Additional type aliases (Props, PropsResult, MiddlewareResult, MiddlewareMap)
# are available from tdom_svcs.types for users who need them.

__all__ = [
    "Component",
    "component",
    "execute_component_middleware",
    "execute_middleware",
    "execute_middleware_async",
    "get_component_middleware",
    "html",
    "middleware",
    "register_middleware",
    "scan",
]
