from collections.abc import Coroutine
from typing import Any, Callable, Protocol, TypeVar, runtime_checkable

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

type MiddlewareMap = dict[str, list["Middleware"]]
"""Mapping of lifecycle phases to middleware lists for per-component middleware."""

T = TypeVar("T")


@runtime_checkable
class DIContainer(Protocol):
    """
    Protocol for dependency injection containers.

    This protocol abstracts dependency injection container implementations,
    allowing any container (svcs.Container, etc.) to be used with tdom-svcs
    without tight coupling.

    Examples:
        # svcs.Container satisfies this protocol
        >>> import svcs
        >>> registry = svcs.Registry()
        >>> container = svcs.Container(registry)
        >>> isinstance(container, DIContainer)  # Would be True at runtime

        # Custom container implementation
        >>> class MyContainer:
        ...     def get(self, service_type):
        ...         return service_type()
        >>> my_container = MyContainer()
        >>> # Can be used with tdom-svcs DI system
    """

    def get(self, service_type: type[T]) -> T:
        """
        Resolve and return an instance of the requested service type.

        Args:
            service_type: The type/class to resolve

        Returns:
            Instance of the requested type

        Raises:
            ServiceNotFoundError or similar: If service cannot be resolved
        """
        ...


def is_di_container(obj: Any) -> bool:
    """
    Check if obj is a proper DI container (not just a dict with .get()).

    The DIContainer protocol is @runtime_checkable, but a plain dict would
    pass isinstance() since it has a .get() method. This function explicitly
    excludes dicts to avoid false positives.

    Args:
        obj: Object to check

    Returns:
        True if obj is a DI container, False otherwise
    """
    if isinstance(obj, dict):
        return False
    return isinstance(obj, DIContainer)


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
        props: Props,
        context: Context,
    ) -> MiddlewareResult: ...
