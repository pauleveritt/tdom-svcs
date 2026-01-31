"""Middleware system for component lifecycle hooks."""

from tdom_svcs.types import Context, Middleware

from .decorators import component, get_component_middleware, register_component
from .exceptions import (
    ContextNotSetupError,
    MiddlewareConfigurationError,
    MiddlewareError,
    MiddlewareExecutionError,
)
from .middleware_manager import MiddlewareManager


def setup_container(
    context: object, registry: object | None = None, register_manager: bool = True
) -> None:
    """
    Setup context for middleware system with service registration.

    This utility function validates and registers the context object to make it
    available to middleware during execution. The context can be any dict-like
    object that satisfies the Context protocol.

    By default, registers MiddlewareManager as a service (register_manager=True),
    enabling dependency injection of the manager itself into other services. This
    is the recommended pattern for most applications.

    Usage patterns:
        # With plain dict (validation only)
        >>> context = {"logger": logger_instance, "config": config}
        >>> setup_container(context)
        >>> # Context dict is validated and ready to use

        # With svcs.Registry (validation + context registration)
        >>> import svcs
        >>> registry = svcs.Registry()
        >>> context = {"logger": logger_instance}
        >>> setup_container(context, registry)
        >>> # Context is registered with registry for dependency injection
        >>> container = svcs.Container(registry)
        >>> retrieved = container.get(Context)  # Gets the context dict

        # With MiddlewareManager service registration
        >>> registry = svcs.Registry()
        >>> context = {"config": {"debug": True}}
        >>> setup_container(context, registry, register_manager=True)
        >>> # Both Context and MiddlewareManager are now available as services
        >>> container = svcs.Container(registry)
        >>> manager = container.get(MiddlewareManager)  # Gets manager via DI

        # With custom dict-like object
        >>> class CustomContext:
        ...     def __getitem__(self, key): ...
        ...     def get(self, key, default=None): ...
        >>> custom = CustomContext()
        >>> setup_container(custom)

    Implementation details:
        - Validates that context satisfies Context protocol (has __getitem__ and get())
        - If registry provided and has register_value method, registers context via
          registry.register_value(Context, context, enter=False)
        - If register_manager=True, registers MiddlewareManager factory with registry
        - For plain dict or custom objects without registry, just validates protocol
        - Should be called during app initialization before rendering
        - No hard dependency on svcs/svcs-di - works with any dict-like context

    Args:
        context: Dict-like context object satisfying Context protocol.
                Must have __getitem__ and get() methods.
        registry: Optional registry object with register_value() and register_factory() methods.
                 If provided, context will be registered for DI and MiddlewareManager will
                 be registered as a service (unless register_manager=False).
        register_manager: If True and registry provided, register MiddlewareManager as a service.
                         Default is True. Set to False to skip manager registration.

    Raises:
        TypeError: If context doesn't satisfy Context protocol
        MiddlewareConfigurationError: If registration fails

    Example:
        >>> import svcs
        >>> from tdom_svcs.services.middleware import setup_container, MiddlewareManager
        >>>
        >>> # Setup during app initialization (manager registered by default)
        >>> registry = svcs.Registry()
        >>> context = {"config": {"debug": True}}
        >>> setup_container(context, registry)
        >>>
        >>> # Both Context and MiddlewareManager available via DI
        >>> container = svcs.Container(registry)
        >>> manager = container.get(MiddlewareManager)
        >>> # Register middleware that uses context...
    """
    # Validate context satisfies Context protocol
    if not isinstance(context, Context):
        raise TypeError(
            f"Object of type {type(context).__name__} does not satisfy "
            f"Context protocol. Context must have '__getitem__(key: str) -> Any' "
            f"and 'get(key: str, default: Any = None) -> Any' methods."
        )

    # If registry provided, register the context for dependency injection
    if registry is None:
        # For plain dict or custom contexts without registry, caller must pass
        # the same context object directly to MiddlewareManager.execute()
        return

    # Validate registry has required methods
    if not hasattr(registry, "register_value"):
        raise TypeError(
            f"Registry of type {type(registry).__name__} does not have "
            f"'register_value' method. Expected svcs.Registry or compatible object."
        )
    if register_manager and not hasattr(registry, "register_factory"):
        raise TypeError(
            f"Registry of type {type(registry).__name__} does not have "
            f"'register_factory' method required for manager registration."
        )

    # Register context with registry
    try:
        registry.register_value(Context, context, enter=False)  # type: ignore[attr-defined]
    except Exception as e:
        raise MiddlewareConfigurationError(
            f"Failed to register context with registry: {e}"
        ) from e

    # Optionally register MiddlewareManager as a service
    if register_manager:
        try:
            registry.register_factory(  # type: ignore[attr-defined]
                MiddlewareManager, MiddlewareManager, enter=False
            )
        except Exception as e:
            raise MiddlewareConfigurationError(
                f"Failed to register MiddlewareManager with registry: {e}"
            ) from e


__all__ = [
    # Protocols
    "Context",
    "Middleware",
    # Manager
    "MiddlewareManager",
    # Utilities
    "setup_container",
    # Decorators
    "component",
    "register_component",
    "get_component_middleware",
    # Exceptions
    "MiddlewareError",
    "MiddlewareExecutionError",
    "MiddlewareConfigurationError",
    "ContextNotSetupError",
]
