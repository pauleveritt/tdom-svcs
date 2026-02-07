# API Reference

Complete API documentation for tdom-svcs.

## Core Functions

### scan()

```python
def scan(
    registry: svcs.Registry,
    *package_names: str,
) -> None:
    """
    Scan packages for @injectable components and register them.

    Discovers all classes decorated with @injectable in the specified packages
    and registers them in svcs.Registry (for DI).

    Args:
        registry: The svcs.Registry to register components in for DI
        *package_names: One or more package names to scan

    Raises:
        ImportError: If a package cannot be imported
        ValueError: If package structure is invalid

    Example:
        >>> from svcs_di.injectors.locator import scan
        >>> registry = svcs.Registry()
        >>> scan(registry, "myapp.components")
    """
```

**See also:** {doc}`core_concepts` for usage examples.

### html()

```python
def html(
    template: Template,
    *,
    context: DIContainer | dict[str, Any] | None = None,
    config: dict[str, Any] | None = None,
) -> Markup:
    """
    Render a tdom template with automatic dependency injection.

    This is the main entry point for rendering tdom templates with tdom-svcs.
    It wraps the standard tdom html() function and adds DI support.

    Args:
        template: PEP 750 template string (t"...")
        context: DI container or dict passed to components
        config: Additional configuration dict

    Returns:
        Markup: Rendered HTML markup

    Example:
        >>> result = html(t"<{Button} label='Submit' />", context=container)
        >>> str(result)
        '<button>Submit</button>'
    """
```

**See also:** {doc}`getting_started` for basic usage.

## Decorators

### @middleware

```python
def middleware(
    cls: type | None = None,
    *,
    categories: list[str] | None = None,
) -> type:
    """
    Decorator to mark a class as middleware.

    Automatically registers the class as middleware and assigns categories.
    The 'middleware' category is always added automatically.

    Args:
        cls: The middleware class to decorate
        categories: Additional categories for organization

    Example:
        >>> @middleware(categories=["security", "auth"])
        ... @dataclass
        ... class AuthMiddleware:
        ...     priority: int = -10
        ...     def __call__(self, component, props, context):
        ...         return props
    """
```

**See also:** {doc}`services/middleware` for middleware documentation.

### @component

```python
def component(
    cls: type | None = None,
    *,
    middleware: dict[str, list[type]] | None = None,
    categories: list[str] | None = None,
) -> type:
    """
    Decorator to mark a class as a component with optional per-component middleware.

    Automatically assigns categories and attaches middleware configuration.
    The 'component' category is always added automatically.

    Args:
        cls: The component class to decorate
        middleware: Per-component middleware configuration
        categories: Additional categories for organization

    Example:
        >>> @component(
        ...     middleware={"pre_resolution": [ValidationMiddleware]},
        ...     categories=["page", "admin"]
        ... )
        ... @dataclass
        ... class AdminDashboard:
        ...     title: str = "Admin"
    """
```

**See also:** {doc}`core_concepts` for component patterns.

## Registration Functions

### register_middleware()

```python
def register_middleware(
    registry: HopscotchRegistry,
    middleware_type: type,
    *,
    categories: list[str] | None = None,
) -> None:
    """
    Imperatively register a middleware type with the registry.

    Automatically registers a factory for the middleware if one doesn't exist.
    Assigns the 'middleware' category plus any additional categories.

    Args:
        registry: Registry to register in
        middleware_type: The middleware class type
        categories: Additional categories for organization

    Example:
        >>> register_middleware(
        ...     registry,
        ...     SecurityMiddleware,
        ...     categories=["security", "compliance"]
        ... )
    """
```

### register_component()

```python
def register_component(
    registry: HopscotchRegistry,
    component_type: type,
    *,
    middleware: dict[str, list[type]] | None = None,
    categories: list[str] | None = None,
) -> None:
    """
    Imperatively register a component type with the registry.

    Automatically registers a factory for the component if one doesn't exist.
    Assigns the 'component' category plus any additional categories.
    Attaches middleware configuration to the component class.

    Args:
        registry: Registry to register in
        component_type: The component class type
        middleware: Per-component middleware configuration
        categories: Additional categories for organization

    Example:
        >>> register_component(
        ...     registry,
        ...     SecurePage,
        ...     middleware={"pre_resolution": [AuthMiddleware]},
        ...     categories=["page", "protected"]
        ... )
    """
```

## Execution Functions

### execute_middleware()

```python
def execute_middleware(
    component: type | Callable[..., Any],
    props: dict[str, Any],
    container: svcs.Container,
) -> dict[str, Any] | None:
    """
    Execute global middleware chain for a component.

    Retrieves registered middleware from the container and executes them
    in priority order (lowest priority number first).

    Args:
        component: Component being processed
        props: Props to pass through middleware
        container: DI container for resolving middleware

    Returns:
        Modified props, or None if middleware halts execution

    Raises:
        RuntimeError: If async middleware detected in sync execution

    Example:
        >>> props = {"label": "Click"}
        >>> result = execute_middleware(Button, props, container)
        >>> assert result["label"] == "Click"
    """
```

### execute_middleware_async()

```python
async def execute_middleware_async(
    component: type | Callable[..., Any],
    props: dict[str, Any],
    container: svcs.Container,
) -> dict[str, Any] | None:
    """
    Execute middleware chain with async support.

    Automatically handles both sync and async middleware, awaiting
    async middleware calls.

    Args:
        component: Component being processed
        props: Props to pass through middleware
        container: DI container for resolving middleware

    Returns:
        Modified props, or None if middleware halts execution

    Example:
        >>> props = {"user_id": 123}
        >>> result = await execute_middleware_async(Dashboard, props, container)
    """
```

### execute_component_middleware()

```python
def execute_component_middleware(
    component_type: type,
    props: dict[str, Any],
    container: svcs.Container,
    phase: str = "pre_resolution",
) -> dict[str, Any] | None:
    """
    Execute per-component middleware for a specific lifecycle phase.

    Reads middleware configuration from the component class's
    COMPONENT_MIDDLEWARE_ATTR and executes specified middleware.

    Args:
        component_type: Component class with middleware config
        props: Props to pass through middleware
        container: DI container for resolving middleware
        phase: Lifecycle phase ("pre_resolution", "post_resolution", etc.)

    Returns:
        Modified props, or None if middleware halts execution

    Example:
        >>> result = execute_component_middleware(
        ...     AdminDashboard,
        ...     props,
        ...     container,
        ...     phase="pre_resolution"
        ... )
    """
```

## Category Functions

### list_categories()

Available on `HopscotchRegistry`:

```python
def list_categories(self) -> set[str]:
    """
    List all categories registered in the registry.

    Returns:
        Set of all category names

    Example:
        >>> categories = registry.list_categories()
        >>> assert "middleware" in categories
        >>> assert "component" in categories
    """
```

### get_by_category()

Available on `HopscotchRegistry`:

```python
def get_by_category(self, category: str) -> Iterator[type]:
    """
    Get all items (middleware/components) in a specific category.

    Args:
        category: Category name to query

    Yields:
        Types registered in the category

    Example:
        >>> for mw_type in registry.get_by_category("security"):
        ...     print(mw_type.__name__)
    """
```

### get_categories()

Available on `HopscotchRegistry`:

```python
def get_categories(self, item_type: type) -> tuple[str, ...]:
    """
    Get all categories assigned to a specific item.

    Args:
        item_type: The class type to check

    Returns:
        Tuple of category names

    Example:
        >>> categories = registry.get_categories(AuthMiddleware)
        >>> assert "middleware" in categories
        >>> assert "security" in categories
    """
```

### has_category()

Available on `HopscotchRegistry`:

```python
def has_category(self, item_type: type, category: str) -> bool:
    """
    Check if an item has a specific category.

    Args:
        item_type: The class type to check
        category: Category name to check for

    Returns:
        True if item has the category

    Example:
        >>> if registry.has_category(AuthMiddleware, "security"):
        ...     print("Is a security middleware")
    """
```

**See also:** {doc}`categories` for category system documentation.

## Introspection Functions

### list_middlewares()

```python
def list_middlewares(registry: HopscotchRegistry) -> tuple[MiddlewareInfo, ...]:
    """
    List all registered middleware with metadata.

    Returns immutable tuple of MiddlewareInfo objects containing
    middleware type, priority, and categories.

    Args:
        registry: Registry to introspect

    Returns:
        Tuple of MiddlewareInfo objects

    Example:
        >>> for info in list_middlewares(registry):
        ...     print(f"{info.middleware_type.__name__}: {info.priority}")
    """
```

### list_components()

```python
def list_components(registry: HopscotchRegistry) -> tuple[ComponentInfo, ...]:
    """
    List all registered components with variations.

    Returns immutable tuple of ComponentInfo objects containing
    service type, variations, and categories.

    Args:
        registry: Registry to introspect

    Returns:
        Tuple of ComponentInfo objects

    Example:
        >>> for info in list_components(registry):
        ...     print(f"{info.service_type.__name__}: {len(info.variations)} variations")
    """
```

**See also:** {doc}`services/introspection` for introspection documentation.

## Core Classes



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

### scan

```python
def scan(
    registry: svcs.Registry,
    *package_names: str,
) -> None
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
- {doc}`services/middleware` - MiddlewareManager details
- {doc}`examples/index` - Working examples
