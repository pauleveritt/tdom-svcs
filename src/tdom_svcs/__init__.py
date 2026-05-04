"""tdom-svcs: Dependency injection for tdom templates."""

from tdom_svcs.middleware import (
    AsyncMiddleware,
    HOOKABLE_MIDDLEWARE_ATTR,
    Middleware,
    execute_middleware,
    execute_middleware_async,
    execute_target_middleware,
    hookable,
    middleware,
    register_hookable,
    register_middleware,
)
from tdom_svcs.types import (
    AnyMiddleware,
    MiddlewareMap,
    Props,
    PropsResult,
    Target,
)

# Local tdom-specific functionality
from tdom_svcs.introspection import (
    ComponentInfo,
    ComponentMap,
    ComponentVariation,
    MiddlewareInfo,
    list_components,
    list_middlewares,
)
from tdom_svcs.processor import html
from tdom_svcs.scanning import scan

__all__ = [
    "AsyncMiddleware",
    "AnyMiddleware",
    "HOOKABLE_MIDDLEWARE_ATTR",
    "Middleware",
    "MiddlewareMap",
    "Props",
    "PropsResult",
    "Target",
    "execute_middleware",
    "execute_middleware_async",
    "execute_target_middleware",
    "hookable",
    "middleware",
    "register_hookable",
    "register_middleware",
    # tdom-specific functionality
    "ComponentInfo",
    "ComponentMap",
    "ComponentVariation",
    "MiddlewareInfo",
    "html",
    "list_components",
    "list_middlewares",
    "scan",
]
