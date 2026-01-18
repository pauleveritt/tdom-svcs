"""Implementation of middleware manager service."""

import inspect
import threading
from dataclasses import dataclass, field
from operator import attrgetter
from typing import Any, cast

from tdom_svcs.types import Component

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
        # Validate container is not a plain dict and has callable get() method
        # Plain dicts have get() but resolve keys, not services
        if isinstance(container, dict):
            raise TypeError(
                "Container cannot be a plain dict. "
                "Expected svcs.Container or compatible service container."
            )
        if not (hasattr(container, "get") and callable(container.get)):
            raise TypeError(
                f"Container of type {type(container).__name__} does not have "
                f"callable 'get()' method required for service resolution. "
                f"Expected svcs.Container or compatible service container."
            )

        with self._lock:
            self._middleware_services.append((middleware_type, container))

    def _resolve_middleware_service(
        self, middleware_type: type[Middleware], container: Any
    ) -> Middleware:
        """
        Resolve a single middleware service from container.

        Args:
            middleware_type: The middleware class to resolve
            container: Container to resolve from

        Returns:
            Resolved middleware instance

        Raises:
            RuntimeError: If resolution or validation fails
        """
        try:
            middleware_instance = container.get(middleware_type)
        except Exception as e:
            raise RuntimeError(
                f"Failed to resolve middleware service {middleware_type.__name__} "
                f"from container: {e}"
            ) from e

        # Validate it satisfies protocol
        if not isinstance(middleware_instance, Middleware):
            raise RuntimeError(
                f"Service {middleware_type.__name__} does not satisfy "
                f"Middleware protocol after resolution from container."
            )

        return middleware_instance

    def _resolve_all_middleware(self) -> list[Middleware]:
        """
        Resolve all middleware (both direct instances and services).

        Returns a combined list of middleware from both direct registration
        and service-based registration, sorted by priority.

        Thread safety: Copies data structures inside lock, then resolves
        services outside lock to avoid holding lock during potentially
        slow container.get() operations.

        Returns:
            List of middleware instances sorted by priority (lower first)
        """
        # Copy data structures inside lock to minimize lock contention
        with self._lock:
            direct_middleware = list(self._middleware)
            service_registrations = list(self._middleware_services)

        # Resolve services outside lock to avoid blocking during container.get()
        # Use comprehension for cleaner code
        service_instances = [
            self._resolve_middleware_service(middleware_type, container)
            for middleware_type, container in service_registrations
        ]

        # Combine and sort by priority (lower numbers first)
        all_middleware = direct_middleware + service_instances
        return sorted(all_middleware, key=attrgetter("priority"))

    def _execute_middleware_chain(
        self,
        sorted_middleware: list[Middleware],
        component: Component,
        props: dict[str, Any],
        context: Context,
    ) -> dict[str, Any] | None:
        """
        Execute middleware chain synchronously.

        Args:
            sorted_middleware: List of middleware sorted by priority
            component: Component being processed
            props: Initial props dict
            context: Execution context

        Returns:
            Final props dict or None if halted

        Raises:
            RuntimeError: If async middleware detected in sync execution
        """
        current_props = props
        for middleware in sorted_middleware:
            # Check if middleware is async
            if inspect.iscoroutinefunction(middleware.__call__):
                raise RuntimeError(
                    f"Async middleware {type(middleware).__name__} detected in "
                    f"synchronous execution. Use execute_async() instead."
                )

            # Type checker: after iscoroutinefunction check, we know result is not a coroutine
            result = cast(
                dict[str, Any] | None, middleware(component, current_props, context)
            )

            # Halt if middleware returns None
            if result is None:
                return None

            current_props = result

        return current_props

    async def _execute_middleware_chain_async(
        self,
        sorted_middleware: list[Middleware],
        component: Component,
        props: dict[str, Any],
        context: Context,
    ) -> dict[str, Any] | None:
        """
        Execute middleware chain asynchronously.

        Supports both sync and async middleware with automatic detection.

        Args:
            sorted_middleware: List of middleware sorted by priority
            component: Component being processed
            props: Initial props dict
            context: Execution context

        Returns:
            Final props dict or None if halted
        """
        current_props = props
        for middleware in sorted_middleware:
            # Check if middleware is async
            if inspect.iscoroutinefunction(middleware.__call__):
                # Type checker needs help understanding async call returns coroutine
                coro = middleware(component, current_props, context)
                result = await coro  # type: ignore[misc]
            else:
                # Type checker: after iscoroutinefunction check, we know result is not a coroutine
                result = cast(
                    dict[str, Any] | None,
                    middleware(component, current_props, context),
                )

            # Halt if middleware returns None
            if result is None:
                return None

            current_props = result

        return current_props

    def execute(
        self,
        component: Component,
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
        sorted_middleware = self._resolve_all_middleware()
        return self._execute_middleware_chain(
            sorted_middleware, component, props, context
        )

    async def execute_async(
        self,
        component: Component,
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
        sorted_middleware = self._resolve_all_middleware()
        return await self._execute_middleware_chain_async(
            sorted_middleware, component, props, context
        )
