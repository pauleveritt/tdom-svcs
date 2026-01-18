from collections.abc import Coroutine
from typing import Any, Callable, Protocol, TypeVar, runtime_checkable

type Component = type | Callable[..., Any]

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
