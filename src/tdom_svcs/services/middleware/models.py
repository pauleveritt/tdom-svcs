"""
Middleware protocol definitions.

This module re-exports Context and Middleware protocols from tdom_svcs.types
for convenience when working with the middleware system. Both imports are
equivalent:

    from tdom_svcs.services.middleware.models import Context, Middleware
    from tdom_svcs.types import Context, Middleware

The protocols are defined in tdom_svcs.types to avoid circular dependencies
and make them available throughout the codebase.
"""

from tdom_svcs.types import Context, Middleware

__all__ = ["Context", "Middleware"]
