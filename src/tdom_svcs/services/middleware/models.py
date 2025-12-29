"""Protocol definitions for middleware system."""

from typing import Any, Callable, Protocol, runtime_checkable


@runtime_checkable
class Context(Protocol):
    """
    Protocol for dict-like context access in middleware.

    Context defines a minimal dict-like retrieval interface that middleware
    can use to access dependencies and state. This protocol works with any
    dict-like object including svcs.Container, plain Python dict, or custom
    implementations.

    The protocol is independent of any specific DI framework and uses structural
    subtyping - implementations don't need to inherit from this protocol.

    Examples:
        # Works with svcs.Container
        container = svcs.Container()
        # container satisfies Context protocol

        # Works with plain dict
        context = {"logger": logger_instance}
        # dict satisfies Context protocol

        # Middleware uses dict-like access
        logger = context["logger"]
        config = context.get("config", default_config)
    """

    def __getitem__(self, key: str) -> Any:
        """
        Retrieve value by key from context.

        Args:
            key: String key to retrieve

        Returns:
            Value associated with key

        Raises:
            KeyError: If key is not found in context
        """
        ...

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve value by key with optional default.

        Args:
            key: String key to retrieve
            default: Default value if key not found (default: None)

        Returns:
            Value associated with key, or default if key not found
        """
        ...


@runtime_checkable
class Middleware(Protocol):
    """
    Protocol for middleware that wraps component lifecycle phases.

    Middleware provides a pluggable interface for logging, validation,
    transformation, and error handling during component initialization and
    rendering. Middleware executes in priority order before component resolution.

    The protocol is independent of any specific DI framework and uses structural
    subtyping - implementations don't need to inherit from this protocol.

    Middleware execution:
        - Middleware executes in priority order (lower numbers first)
        - Each middleware receives the component, its props, and context
        - Middleware can modify props and pass them to the next middleware
        - Returning None halts the execution chain immediately
        - Middleware can detect component type via isinstance(component, type)

    Priority range:
        - Range: -100 to +100
        - Default: 0
        - Lower numbers execute first
        - Example: logging (-10), validation (0), transformation (10)

    Component type detection:
        - isinstance(component, type) is True for class components
        - isinstance(component, type) is False for function components
        - Single protocol works for both types - no separate protocols needed

    Examples:
        # Class-based middleware
        @dataclass
        class LoggingMiddleware:
            priority: int = -10

            def __call__(
                self,
                component: type | Callable[..., Any],
                props: dict[str, Any],
                context: Context
            ) -> dict[str, Any] | None:
                if isinstance(component, type):
                    print(f"Class component: {component.__name__}")
                else:
                    print(f"Function component: {component.__name__}")
                return props  # Continue execution

        # Function-based middleware (via wrapper class)
        class ValidationMiddleware:
            priority: int = 0

            def __call__(
                self,
                component: type | Callable[..., Any],
                props: dict[str, Any],
                context: Context
            ) -> dict[str, Any] | None:
                if not props.get("required_field"):
                    return None  # Halt execution
                return props  # Continue execution
    """

    priority: int

    def __call__(
        self,
        component: type | Callable[..., Any],
        props: dict[str, Any],
        context: Context,
    ) -> dict[str, Any] | None:
        """
        Execute middleware on component with props.

        Args:
            component: Component class (type) or function (Callable) being processed.
                      Use isinstance(component, type) to detect: True for classes,
                      False for functions.
            props: Dictionary of component properties that can be modified.
                   Modifications are passed to the next middleware or to the component.
            context: Dict-like context for accessing dependencies and state.
                    Can be svcs.Container, plain dict, or any Context protocol implementation.

        Returns:
            Modified props dict to continue execution chain, or None to halt immediately.
            When returning None, middleware should raise an appropriate exception.

        Examples:
            # Detect component type
            if isinstance(component, type):
                # component is a class - can access __name__, __init__, etc.
                print(f"Processing class: {component.__name__}")
            else:
                # component is a function - can access __name__, parameters, etc.
                print(f"Processing function: {component.__name__}")

            # Modify props
            props["timestamp"] = time.time()
            return props  # Continue to next middleware

            # Halt execution
            if validation_failed:
                raise ValidationError("Props validation failed")
                return None  # Halt chain
        """
        ...
