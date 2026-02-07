"""Middleware system for component lifecycle hooks.

This module provides per-component middleware via decorators.
For global middleware, use the top-level tdom_svcs.middleware module instead.
"""

from tdom_svcs.types import Context, Middleware

from .decorators import component, register_component
from .exceptions import (
    ContextNotSetupError,
    MiddlewareConfigurationError,
    MiddlewareError,
    MiddlewareExecutionError,
)

__all__ = [
    # Protocols
    "Context",
    "Middleware",
    # Decorators (per-component middleware)
    "component",
    "register_component",
    # Exceptions
    "MiddlewareError",
    "MiddlewareExecutionError",
    "MiddlewareConfigurationError",
    "ContextNotSetupError",
]
