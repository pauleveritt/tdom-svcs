"""Public middleware types for tdom-svcs."""

from collections.abc import Callable
from typing import Any, Protocol, runtime_checkable

type Target = type | Callable[..., Any]
"""A target being processed, either a class or a callable."""

type Props = dict[str, Any]
"""Properties passed through a middleware chain."""

type PropsResult = Props | None
"""Middleware result: modified props, or None to halt the chain."""


@runtime_checkable
class Middleware(Protocol):
    """Protocol for synchronous middleware."""

    priority: int

    def __call__(self, target: Target, props: Props, context: Any) -> PropsResult:
        """Execute middleware logic."""
        ...


@runtime_checkable
class AsyncMiddleware(Protocol):
    """Protocol for asynchronous middleware."""

    priority: int

    async def __call__(self, target: Target, props: Props, context: Any) -> PropsResult:
        """Execute async middleware logic."""
        ...


type MiddlewareMap = dict[str, list[type[Middleware]]]
"""Maps phase names to middleware classes."""

type AnyMiddleware = Middleware | AsyncMiddleware
"""Sync or async middleware."""
