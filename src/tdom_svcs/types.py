from collections.abc import Coroutine
from typing import Any, Callable, Protocol, TypeGuard, TypeVar, runtime_checkable

# -------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------

MIDDLEWARE_CATEGORY = "middleware"
"""Default category automatically assigned to all middleware."""

COMPONENT_CATEGORY = "component"
"""Default category automatically assigned to all components."""

COMPONENT_LOCATION_PROP = "_component_location"
"""Internal prop key for storing component location during rendering."""

# -------------------------------------------------------------------------
# Type Aliases
# -------------------------------------------------------------------------

type Component = type | Callable[..., Any]
"""A component can be a class or a callable function."""

type Props = dict[str, Any]
"""Component properties passed to middleware and component callables."""

type PropsResult = Props | None
"""Result from synchronous middleware execution - either props dict or None to halt."""

type MiddlewareResult = PropsResult | Coroutine[Any, Any, PropsResult]
"""Full middleware return type - sync result or async coroutine returning result."""

type MiddlewareMap = dict[str, list[type["Middleware"]]]
"""Mapping of lifecycle phases to middleware types for per-component middleware.

Middleware types are resolved from the DI container at execution time."""

T = TypeVar("T")


@runtime_checkable
class DIContainer(Protocol):
    """Protocol for dependency injection containers."""

    def get(self, service_type: type[T]) -> T:
        """Resolve and return an instance of the requested service type."""
        ...


def is_di_container(obj: object) -> TypeGuard[DIContainer]:
    """Check if obj is a proper DI container (excludes dicts)."""
    if isinstance(obj, dict):
        return False
    return isinstance(obj, DIContainer)


@runtime_checkable
class Context(Protocol):
    """Protocol for dict-like context access in middleware."""

    def __getitem__(self, key: str) -> Any: ...
    def get(self, key: str, default: Any = None) -> Any: ...


@runtime_checkable
class Middleware(Protocol):
    """Protocol for synchronous middleware that wraps component lifecycle phases."""

    priority: int

    def __call__(
        self,
        component: Component,
        props: Props,
        context: Context,
    ) -> PropsResult: ...


@runtime_checkable
class AsyncMiddleware(Protocol):
    """Protocol for asynchronous middleware that wraps component lifecycle phases."""

    priority: int

    async def __call__(
        self,
        component: Component,
        props: Props,
        context: Context,
    ) -> PropsResult: ...


# Union type for middleware registration
type AnyMiddleware = Middleware | AsyncMiddleware
"""Either sync or async middleware - use for registration functions."""
