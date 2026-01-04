from collections.abc import Coroutine
from typing import Any, Callable, Protocol, runtime_checkable

type Component = type | Callable[..., Any]


@runtime_checkable
class Context(Protocol):
    """
    Protocol for dict-like context access in middleware.
    """

    def __getitem__(self, key: str) -> Any: ...
    def get(self, key: str, default: Any = None) -> Any: ...


@runtime_checkable
class Middleware(Protocol):
    """
    Protocol for middleware that wraps component lifecycle phases.
    """

    priority: int

    def __call__(
        self,
        component: Component,
        props: dict[str, Any],
        context: Context,
    ) -> dict[str, Any] | None | Coroutine[Any, Any, dict[str, Any] | None]: ...
