"""tdom-svcs: Dependency injection for tdom templates."""

# Re-export middleware machinery from svcs-di
from svcs_di.middleware import (
    AsyncMiddleware,
    Middleware,
    execute_middleware,
    execute_middleware_async,
    execute_target_middleware,
    hookable,
    middleware,
    register_hookable,
    register_middleware,
)

# Local tdom-specific functionality
from tdom_svcs.introspection import (
    ComponentInfo,
    ComponentVariation,
    MiddlewareInfo,
    list_components,
    list_middlewares,
)
from tdom_svcs.processor import html
from tdom_svcs.scanning import scan

__all__ = [
    # Middleware (re-exported from svcs-di)
    "AsyncMiddleware",
    "Middleware",
    "execute_middleware",
    "execute_middleware_async",
    "execute_target_middleware",
    "hookable",
    "middleware",
    "register_hookable",
    "register_middleware",
    # tdom-specific functionality
    "ComponentInfo",
    "ComponentVariation",
    "MiddlewareInfo",
    "html",
    "list_components",
    "list_middlewares",
    "scan",
]
