"""Implementation of middleware manager service."""

import inspect
import threading
from dataclasses import dataclass, field
from typing import Any, Callable

from .models import Context, Middleware


@dataclass
class MiddlewareManager:
    """
    Thread-safe service for middleware registration and execution.

    MiddlewareManager is a service that maintains a collection of stateless middleware
    registered at startup and executes them in priority order during component lifecycle
    phases. It's designed to be thread-safe for use in free-threaded Python environments.

    As a service, MiddlewareManager provides behavior without business-relevant state.
    It should be registered with svcs.Registry and retrieved via dependency injection.
    Use setup_container() to automatically register this service (enabled by default).

    Middleware can be registered in two ways:
        1. Direct instances: manager.register_middleware(middleware_instance)
        2. Service types: manager.register_middleware_service(MiddlewareType, container)

    Middleware execution:
        - Middleware executes in priority order (lower numbers first)
        - Each middleware receives the component, its props, and context
        - Middleware can modify props and pass them to the next middleware
        - Returning None halts the execution chain immediately
        - Supports both sync and async middleware with automatic detection

    Thread safety:
        - Uses threading.Lock for thread-safe registration
        - Safe for concurrent access in free-threaded Python 3.14+

    Service registration:
        >>> import svcs
        >>> from tdom_svcs.services.middleware import setup_container, MiddlewareManager
        >>> # Setup during app initialization (registers manager as service)
        >>> registry = svcs.Registry()
        >>> context = {"config": {"debug": True}}
        >>> setup_container(context, registry)
        >>> # Get manager via dependency injection
        >>> container = svcs.Container(registry)
        >>> manager = container.get(MiddlewareManager)

    Direct usage:
        >>> from dataclasses import dataclass
        >>> @dataclass
        ... class LoggingMiddleware:
        ...     priority: int = -10
        ...     def __call__(self, component, props, context):
        ...         print(f"Processing {component.__name__}")
        ...         return props
        >>> # Register and use middleware
        >>> manager.register_middleware(LoggingMiddleware())
        >>> props = manager.execute(MyComponent, {"key": "value"}, context)
    """

    _middleware: list[Middleware] = field(default_factory=list, init=False, repr=False)
    _middleware_services: list[tuple[type[Middleware], Any]] = field(
        default_factory=list, init=False, repr=False
    )
    _lock: threading.Lock = field(
        default_factory=threading.Lock, init=False, repr=False
    )

    def register_middleware(self, middleware: Middleware) -> None:
        """
        Register a middleware for execution.

        Middleware are stored in a list and sorted by priority before execution.
        Lower priority numbers execute first (e.g., -10 before 0 before 10).

        Args:
            middleware: The middleware to register (must satisfy Middleware protocol)

        Raises:
            TypeError: If middleware doesn't satisfy Middleware protocol

        Example:
            >>> @dataclass
            ... class ValidationMiddleware:
            ...     priority: int = 0
            ...     def __call__(self, component, props, context):
            ...         if "required_field" not in props:
            ...             return None  # Halt execution
            ...         return props
            >>> manager = MiddlewareManager()
            >>> manager.register_middleware(ValidationMiddleware())
        """
        # Validate middleware satisfies protocol
        if not isinstance(middleware, Middleware):
            raise TypeError(
                f"Object of type {type(middleware).__name__} does not satisfy "
                f"Middleware protocol. Middleware must have 'priority: int' attribute "
                f"and '__call__(component, props, context) -> dict[str, Any] | None' method."
            )

        with self._lock:
            self._middleware.append(middleware)

    def register_middleware_service(
        self, middleware_type: type[Middleware], container: Any
    ) -> None:
        """
        Register a middleware service type for lazy construction via DI.

        This method allows middleware to be registered as services that will be
        constructed from the container during execution. This enables dependency
        injection for middleware themselves - middleware can have their own
        dependencies that are resolved from the container.

        The middleware instance is constructed once per execution (not cached),
        allowing fresh state per middleware chain execution.

        Args:
            middleware_type: The middleware class/type to register
            container: Container with get() method for resolving the middleware

        Raises:
            TypeError: If container doesn't have get() method

        Example:
            >>> from dataclasses import dataclass
            >>> @dataclass
            ... class LoggingMiddleware:
            ...     logger: Logger  # Injected dependency
            ...     priority: int = -10
            ...     def __call__(self, component, props, context):
            ...         self.logger.info(f"Processing {component.__name__}")
            ...         return props
            >>> # Register service in svcs registry
            >>> registry.register_factory(Logger, create_logger)
            >>> registry.register_factory(LoggingMiddleware, LoggingMiddleware)
            >>> container = svcs.Container(registry)
            >>> manager = MiddlewareManager()
            >>> manager.register_middleware_service(LoggingMiddleware, container)
        """
        # Validate container has get() method (and isn't just a dict)
        # We need a service container, not a plain dict
        if isinstance(container, dict) or not (
            hasattr(container, "get") and callable(getattr(container, "get", None))
        ):
            raise TypeError(
                f"Container of type {type(container).__name__} does not have "
                f"'get()' method required for service resolution. "
                f"Expected svcs.Container or compatible service container."
            )

        with self._lock:
            self._middleware_services.append((middleware_type, container))

    def _resolve_all_middleware(self) -> list[Middleware]:
        """
        Resolve all middleware (both direct instances and services).

        Returns a combined list of middleware from both direct registration
        and service-based registration, sorted by priority.

        Returns:
            List of middleware instances sorted by priority (lower first)
        """
        with self._lock:
            # Start with direct instances
            all_middleware = list(self._middleware)

            # Resolve service-based middleware from containers
            for middleware_type, container in self._middleware_services:
                try:
                    middleware_instance = container.get(middleware_type)
                    # Validate it satisfies protocol
                    if not isinstance(middleware_instance, Middleware):
                        raise TypeError(
                            f"Service {middleware_type.__name__} does not satisfy "
                            f"Middleware protocol after resolution from container."
                        )
                    all_middleware.append(middleware_instance)
                except Exception as e:
                    raise RuntimeError(
                        f"Failed to resolve middleware service {middleware_type.__name__} "
                        f"from container: {e}"
                    ) from e

        # Sort by priority (lower numbers first)
        return sorted(all_middleware, key=lambda m: m.priority)

    def execute(
        self,
        component: type | Callable[..., Any],
        props: dict[str, Any],
        context: Context,
    ) -> dict[str, Any] | None:
        """
        Execute middleware chain synchronously for a component.

        Middleware are sorted by priority (lower numbers first) and executed in order.
        Each middleware receives the component, the props (potentially modified by
        previous middleware), and the context.

        If any middleware returns None, execution halts immediately and None is returned.
        Otherwise, the final transformed props dict is returned.

        Note: This method only handles synchronous middleware. If any middleware is
        async, you must use execute_async() instead.

        Args:
            component: Component class (type) or function (Callable) being processed
            props: Dictionary of component properties to transform
            context: Dict-like context for accessing dependencies

        Returns:
            Final transformed props dict, or None if any middleware halted execution

        Example:
            >>> manager = MiddlewareManager()
            >>> # Register middleware...
            >>> result = manager.execute(MyComponent, {"key": "value"}, context)
            >>> if result is None:
            ...     # Middleware halted execution
            ...     pass
        """
        # Resolve all middleware (direct instances + services)
        sorted_middleware = self._resolve_all_middleware()

        # Execute middleware in priority order
        current_props = props
        for middleware in sorted_middleware:
            # Check if middleware is async
            if inspect.iscoroutinefunction(middleware.__call__):
                raise RuntimeError(
                    f"Async middleware {type(middleware).__name__} detected in "
                    f"synchronous execution. Use execute_async() instead."
                )

            result = middleware(component, current_props, context)

            # Halt if middleware returns None
            if result is None:
                return None

            current_props = result

        return current_props

    async def execute_async(
        self,
        component: type | Callable[..., Any],
        props: dict[str, Any],
        context: Context,
    ) -> dict[str, Any] | None:
        """
        Execute middleware chain asynchronously for a component.

        This method supports both sync and async middleware. It automatically detects
        async middleware via inspect.iscoroutinefunction() and awaits them appropriately.

        Middleware are sorted by priority (lower numbers first) and executed in order.
        Each middleware receives the component, the props (potentially modified by
        previous middleware), and the context.

        If any middleware returns None, execution halts immediately and None is returned.
        Otherwise, the final transformed props dict is returned.

        Args:
            component: Component class (type) or function (Callable) being processed
            props: Dictionary of component properties to transform
            context: Dict-like context for accessing dependencies

        Returns:
            Final transformed props dict, or None if any middleware halted execution

        Example:
            >>> manager = MiddlewareManager()
            >>> # Register both sync and async middleware...
            >>> result = await manager.execute_async(MyComponent, {"key": "value"}, context)
            >>> if result is None:
            ...     # Middleware halted execution
            ...     pass
        """
        # Resolve all middleware (direct instances + services)
        sorted_middleware = self._resolve_all_middleware()

        # Execute middleware in priority order
        current_props = props
        for middleware in sorted_middleware:
            # Check if middleware is async
            if inspect.iscoroutinefunction(middleware.__call__):
                # Type checker needs help understanding async call returns coroutine
                coro = middleware(component, current_props, context)
                result = await coro  # type: ignore[misc]
            else:
                result = middleware(component, current_props, context)

            # Halt if middleware returns None
            if result is None:
                return None

            current_props = result

        return current_props
