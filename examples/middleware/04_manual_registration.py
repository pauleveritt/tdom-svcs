"""
Manual Middleware Registration Example.

This example demonstrates using middleware WITHOUT the service pattern:
1. Create MiddlewareManager directly (no DI)
2. Register middleware instances manually
3. Pass context as plain dict
4. No svcs.Registry or Container needed

When to use this pattern:
- Simple applications that don't use dependency injection
- Quick prototyping or scripts
- Testing scenarios where DI adds complexity

When to use service pattern instead (see example 01_basic_middleware.py):
- Applications already using svcs for dependency injection
- When middleware need their own service dependencies
- When you want consistent service lifecycle management
"""

from dataclasses import dataclass
from datetime import datetime
from typing import cast

from tdom_svcs.services.middleware import Context, MiddlewareManager


# Define middleware implementations
@dataclass
class LoggingMiddleware:
    """Simple logging middleware."""

    priority: int = -10

    def __call__(self, component, props, context):
        """Log component processing."""
        component_name = (
            component.__name__ if hasattr(component, "__name__") else str(component)
        )
        print(f"[LOG] Processing {component_name}")
        return props


@dataclass
class TimestampMiddleware:
    """Add timestamp to props."""

    priority: int = 0

    def __call__(self, component, props, context):
        """Add processing timestamp."""
        props["processed_at"] = datetime.now().isoformat()
        return props


@dataclass
class DebugMiddleware:
    """Debug middleware that checks context."""

    priority: int = 10

    def __call__(self, component, props, context):
        """Print debug info from context."""
        debug = context.get("debug", False)
        if debug:
            print(f"[DEBUG] Props: {props}")
            print(f"[DEBUG] Context keys: {list(context.keys())}")
        return props


# Example component
class Button:
    """Example component."""

    def __init__(self, title: str, **kwargs):
        self.title = title
        self.props = kwargs


def main():
    """Demonstrate manual middleware registration without services."""
    print("=== Manual Middleware Registration Example ===\n")

    # 1. Create manager directly (no DI)
    print("Creating MiddlewareManager directly...")
    manager = MiddlewareManager()
    print("✓ Manager created\n")

    # 2. Register middleware instances manually
    print("Registering middleware...")
    manager.register_middleware(LoggingMiddleware())
    manager.register_middleware(TimestampMiddleware())
    manager.register_middleware(DebugMiddleware())
    print("✓ Registered 3 middleware\n")

    # 3. Create context as plain dict (no svcs)
    print("Creating context as plain dict...")
    context: Context = cast(
        Context,
        {
            "debug": True,
            "user": "admin",
            "request_id": "12345",
        },
    )
    print(f"✓ Context: {dict(context)}\n")  # type: ignore[arg-type]

    # 4. Execute middleware chain
    print("--- Executing middleware chain ---")
    props = {"title": "Click Me", "variant": "primary"}
    result = manager.execute(Button, props, context)

    if result is not None:
        print(f"\n✓ Execution successful!")
        print(f"  Final props: {result}")
    else:
        print("\n✗ Execution halted")

    # 5. Execute without debug
    print("\n\n--- Executing without debug ---")
    # Create new context with debug disabled
    context_no_debug: Context = cast(
        Context,
        {
            "debug": False,
            "user": "admin",
            "request_id": "12345",
        },
    )
    props = {"title": "Submit"}
    result = manager.execute(Button, props, context_no_debug)

    if result is not None:
        print(f"\n✓ Execution successful!")
        print(f"  Final props: {result}")

    print("\n\n=== Example Complete ===")
    print("\nComparison:")
    print("• Manual pattern: Simple, direct, no DI overhead")
    print("• Service pattern: Better for apps with DI, middleware dependencies")
    print("• Choose based on your application's needs!")


if __name__ == "__main__":
    main()
