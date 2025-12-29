"""
Basic Middleware Usage Example.

This example demonstrates the recommended pattern for using middleware as a service:
1. Setup context and register MiddlewareManager as a service (default behavior)
2. Get MiddlewareManager via dependency injection
3. Register middleware instances
4. Execute middleware chain

The middleware service pattern enables:
- Dependency injection for MiddlewareManager
- Consistent service lifecycle management
- Easy testing with fakes
"""

from dataclasses import dataclass
from typing import cast

import svcs

from tdom_svcs.services.middleware import Context, MiddlewareManager, setup_container


# Define middleware implementations
@dataclass
class LoggingMiddleware:
    """Middleware that logs component processing."""

    priority: int = -10  # Run early

    def __call__(self, component, props, context):
        """Log the component being processed."""
        component_name = (
            component.__name__ if hasattr(component, "__name__") else str(component)
        )
        print(f"[LOG] Processing {component_name} with props: {props}")
        return props  # Continue execution


@dataclass
class ValidationMiddleware:
    """Middleware that validates props."""

    priority: int = 0  # Run at default priority

    def __call__(self, component, props, context):
        """Validate that required fields are present."""
        if "title" not in props:
            print("[VALIDATION] Error: 'title' field is required")
            return None  # Halt execution
        print(f"[VALIDATION] Props validated successfully")
        return props  # Continue execution


@dataclass
class TransformationMiddleware:
    """Middleware that transforms props."""

    priority: int = 10  # Run late

    def __call__(self, component, props, context):
        """Add a timestamp to props."""
        from datetime import datetime

        props["processed_at"] = datetime.now().isoformat()
        print(f"[TRANSFORM] Added timestamp: {props['processed_at']}")
        return props  # Continue execution


# Example component
class Button:
    """Example component."""

    def __init__(self, title: str, **kwargs):
        self.title = title
        self.props = kwargs


def main():
    """Demonstrate basic middleware usage with service pattern."""
    print("=== Basic Middleware Service Example ===\n")

    # 1. Setup: Create registry and context
    registry = svcs.Registry()
    context: Context = cast(Context, {"config": {"debug": True}})

    # 2. Setup container (registers MiddlewareManager as service by default)
    print("Setting up container...")
    setup_container(context, registry)
    print("✓ MiddlewareManager registered as a service\n")

    # 3. Get manager via dependency injection
    container = svcs.Container(registry)
    manager = container.get(MiddlewareManager)
    print("✓ Retrieved MiddlewareManager from container\n")

    # 4. Register middleware instances
    print("Registering middleware...")
    manager.register_middleware(LoggingMiddleware())
    manager.register_middleware(ValidationMiddleware())
    manager.register_middleware(TransformationMiddleware())
    print("✓ Registered 3 middleware\n")

    # 5. Execute middleware chain (successful case)
    print("--- Executing with valid props ---")
    props = {"title": "Click Me", "variant": "primary"}
    result = manager.execute(Button, props, context)

    if result is not None:
        print(f"\n✓ Execution successful!")
        print(f"  Final props: {result}\n")
    else:
        print("\n✗ Execution halted by middleware\n")

    # 6. Execute middleware chain (halted case)
    print("--- Executing with invalid props (missing title) ---")
    props = {"variant": "secondary"}
    result = manager.execute(Button, props, context)

    if result is not None:
        print(f"\n✓ Execution successful!")
        print(f"  Final props: {result}\n")
    else:
        print("\n✗ Execution halted by validation middleware\n")

    print("=== Example Complete ===")


if __name__ == "__main__":
    main()
