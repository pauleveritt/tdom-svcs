"""tdom-svcs: Dependency injection for tdom templates."""

from tdom_svcs.processor import html
from tdom_svcs.types import Component

# Note: Additional type aliases (Props, PropsResult, MiddlewareResult, MiddlewareMap)
# are available from tdom_svcs.types for users who need them.

__all__ = [
    "Component",
    "html",
]
