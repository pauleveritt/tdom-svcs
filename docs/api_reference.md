# API Reference

Complete API documentation for tdom-svcs.

## Core Functions

### scan_components()

```python
def scan_components(
    registry: svcs.Registry,
    component_registry: ComponentNameRegistry,
    *package_names: str,
) -> None:
    """
    Scan packages for @injectable components and register them.

    Discovers all classes decorated with @injectable in the specified packages
    and registers them in both svcs.Registry (for DI) and ComponentNameRegistry
    (for name lookup).

    Args:
        registry: The svcs.Registry to register components in for DI
        component_registry: The ComponentNameRegistry for string name mapping
        *package_names: One or more package names to scan

    Raises:
        ImportError: If a package cannot be imported
        ValueError: If package structure is invalid

    Example:
        >>> registry = svcs.Registry()
        >>> component_registry = ComponentNameRegistry()
        >>> scan_components(registry, component_registry, "myapp.components")
    """
```

**See also:** {doc}`core_concepts` for usage examples.

## Core Classes

### ComponentNameRegistry

Thread-safe registry mapping component names to class types.

```python
class ComponentNameRegistry:
    """
    Registry for mapping string component names to class types.

    Provides thread-safe registration and lookup of component types by name.
    Only accepts class types, not functions or other callables.
    """

    def register(self, name: str, component_type: type) -> None:
        """
        Register a component class under a string name.

        Args:
            name: String name for the component (e.g., "Button")
            component_type: The component class type

        Raises:
            TypeError: If component_type is not a class type

        Example:
            >>> registry = ComponentNameRegistry()
            >>> registry.register("Button", Button)
        """

    def get_type(self, name: str) -> type | None:
        """
        Get component class type by name.

        Args:
            name: Component name to look up

        Returns:
            The component class type if registered, None otherwise

        Example:
            >>> button_type = registry.get_type("Button")
            >>> if button_type:
            ...     instance = button_type(label="Click")
        """

    def get_all_names(self) -> list[str]:
        """
        Get all registered component names.

        Returns:
            List of all registered component names

        Example:
            >>> names = registry.get_all_names()
            >>> print(f"Registered: {', '.join(names)}")
        """
```

**See also:** {doc}`services/component_registry` for detailed documentation.

### ComponentLookup

Service for resolving component names to instances with dependency injection.

```python
class ComponentLookup:
    """
    Service for resolving component names to component instances.

    Bridges string-based component references (from templates) to Python
    objects with full dependency injection and middleware support.
    """

    def __init__(self, container: svcs.Container) -> None:
        """
        Initialize ComponentLookup with a container.

        Args:
            container: svcs.Container with registered services

        Example:
            >>> lookup = ComponentLookup(container=container)
        """

    def __call__(
        self,
        component_name: str,
        context: dict[str, Any],
    ) -> Any:
        """
        Resolve component by name with dependency injection.

        Args:
            component_name: String name of component to resolve
            context: Dictionary of context values for non-injected fields

        Returns:
            Constructed component instance (or coroutine for async)

        Raises:
            ComponentNotFoundError: If component name not registered
            InjectorNotFoundError: If required injector not in container
            RegistryNotSetupError: If ComponentNameRegistry not registered

        Example:
            >>> button = lookup("Button", context={"label": "Submit"})
            >>> output = button()
        """
```

**See also:** {doc}`services/component_lookup` for detailed documentation.

### MiddlewareManager

Service for managing and executing middleware lifecycle hooks.

```python
class MiddlewareManager:
    """
    Manager for middleware registration and execution.

    Provides thread-safe middleware registration and ordered execution
    based on middleware priority values.
    """

    def register_middleware(self, middleware: Middleware) -> None:
        """
        Register a middleware instance.

        Args:
            middleware: Middleware instance with priority and __call__

        Raises:
            TypeError: If middleware doesn't satisfy Middleware protocol

        Example:
            >>> manager = MiddlewareManager()
            >>> manager.register_middleware(LoggingMiddleware())
        """

    def register_middleware_service(
        self,
        middleware_type: type,
        container: svcs.Container,
    ) -> None:
        """
        Register middleware as a service with dependency injection.

        Args:
            middleware_type: Middleware class type
            container: Container to get middleware instance from

        Example:
            >>> manager.register_middleware_service(AuthMiddleware, container)
        """

    def execute(
        self,
        component: type,
        props: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any] | None:
        """
        Execute all registered middleware in priority order.

        Args:
            component: Component type being processed
            props: Props to be passed through middleware
            context: Context for middleware execution

        Returns:
            Modified props dict, or None if middleware halts execution

        Example:
            >>> result = manager.execute(Button, {"label": "Click"}, {})
        """

    async def execute_async(
        self,
        component: type,
        props: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any] | None:
        """
        Execute middleware with async support.

        Automatically detects and awaits async middleware while executing
        sync middleware normally.

        Args:
            component: Component type being processed
            props: Props to be passed through middleware
            context: Context for middleware execution

        Returns:
            Modified props dict, or None if middleware halts execution

        Example:
            >>> result = await manager.execute_async(Button, props, context)
        """
```

**See also:** {doc}`services/middleware` for detailed documentation.

## Middleware Utilities

### setup_container()

```python
def setup_container(
    context: Context,
    registry: svcs.Registry,
) -> None:
    """
    Set up container with MiddlewareManager service.

    Convenience function that registers MiddlewareManager as a service
    in the provided registry.

    Args:
        context: Context dictionary for middleware
        registry: svcs.Registry to register MiddlewareManager in

    Example:
        >>> registry = svcs.Registry()
        >>> setup_container({}, registry)
        >>> container = svcs.Container(registry)
        >>> manager = container.get(MiddlewareManager)
    """
```

## Protocols

### Middleware Protocol

```python
class Middleware(Protocol):
    """
    Protocol for middleware objects.

    Middleware must have a priority attribute and implement __call__
    to process component props.
    """

    priority: int
    """
    Execution priority. Lower numbers execute first.
    Common values:
    - -10: Logging, metrics (observe)
    - -5: Authentication, authorization
    - 0: Validation
    - 5: Data enrichment
    - 10: Transformation
    """

    def __call__(
        self,
        component: type | Callable[..., Any],
        props: dict[str, Any],
        context: Context,
    ) -> dict[str, Any] | None:
        """
        Process props before component construction.

        Args:
            component: Component type being processed
            props: Props to process
            context: Context for processing

        Returns:
            Modified props to continue, or None to halt execution
        """
```

## Type Aliases

```python
Context = dict[str, Any]
"""
Context dictionary type for middleware and component resolution.
Contains request-specific data, configuration, etc.
"""
```

## Exceptions

### ComponentNotFoundError

```python
class ComponentNotFoundError(Exception):
    """
    Raised when a component name is not registered in ComponentNameRegistry.

    Attributes:
        component_name: The name that was not found
        available_names: List of registered component names

    Example:
        >>> try:
        ...     component = lookup("Unknown", context={})
        ... except ComponentNotFoundError as e:
        ...     print(f"Not found: {e.component_name}")
        ...     print(f"Available: {e.available_names}")
    """
```

### InjectorNotFoundError

```python
class InjectorNotFoundError(Exception):
    """
    Raised when required injector is not registered in container.

    Indicates setup issue - HopscotchInjector or HopscotchAsyncInjector
    needs to be registered in the svcs.Registry.

    Example:
        >>> try:
        ...     component = lookup("Button", context={})
        ... except InjectorNotFoundError as e:
        ...     print("Register HopscotchInjector in setup")
    """
```

### RegistryNotSetupError

```python
class RegistryNotSetupError(Exception):
    """
    Raised when ComponentNameRegistry is not registered in container.

    Indicates setup issue - ComponentNameRegistry needs to be registered
    as a service in the svcs.Registry.

    Example:
        >>> try:
        ...     component = lookup("Button", context={})
        ... except RegistryNotSetupError as e:
        ...     print("Register ComponentNameRegistry in setup")
    """
```

## Integration with svcs-di

tdom-svcs uses types from `svcs-di` for dependency injection:

### Inject[]

```python
from svcs_di import Inject

# Use Inject[] to mark dependencies
@dataclass
class MyComponent:
    db: Inject[DatabaseService]  # Injected from container
    label: str                    # Regular parameter
```

**See:** [svcs-di documentation](https://github.com/svcs-dev/svcs-di) for details.

### @injectable

```python
from svcs_di.injectors.decorators import injectable

# Mark components for automatic discovery
@injectable
@dataclass
class Button:
    label: str = "Click"
```

**Parameters:**
- `resource`: Resource context for multi-implementation resolution
- `location`: PurePath for location-based resolution

**See:** {doc}`how_it_works` for detailed usage.

### HopscotchInjector

```python
from svcs_di.injectors.locator import HopscotchInjector, HopscotchAsyncInjector

# Register in setup
registry.register_factory(HopscotchInjector, HopscotchInjector)
registry.register_factory(HopscotchAsyncInjector, HopscotchAsyncInjector)
```

**See:** [svcs-di locator documentation](https://github.com/svcs-dev/svcs-di) for details.

## Full Type Signatures

### scan_components

```python
def scan_components(
    registry: svcs.Registry,
    component_registry: ComponentNameRegistry,
    *package_names: str,
) -> None
```

### ComponentNameRegistry

```python
class ComponentNameRegistry:
    def register(self, name: str, component_type: type) -> None
    def get_type(self, name: str) -> type | None
    def get_all_names(self) -> list[str]
```

### ComponentLookup

```python
class ComponentLookup:
    def __init__(self, container: svcs.Container) -> None
    def __call__(self, component_name: str, context: dict[str, Any]) -> Any
```

### MiddlewareManager

```python
class MiddlewareManager:
    def register_middleware(self, middleware: Middleware) -> None
    def register_middleware_service(
        self,
        middleware_type: type,
        container: svcs.Container,
    ) -> None
    def execute(
        self,
        component: type,
        props: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any] | None
    async def execute_async(
        self,
        component: type,
        props: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any] | None
```

## See Also

- {doc}`getting_started` - Installation and quickstart
- {doc}`core_concepts` - Fundamental concepts
- {doc}`how_it_works` - Architecture deep dive
- {doc}`services/component_registry` - ComponentNameRegistry details
- {doc}`services/component_lookup` - ComponentLookup details
- {doc}`services/middleware` - MiddlewareManager details
- {doc}`examples` - Working examples
