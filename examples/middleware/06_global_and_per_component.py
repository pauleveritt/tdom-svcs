"""
Global and Per-Component Middleware Example.

This example demonstrates the comprehensive middleware system:
1. Global middleware registered via MiddlewareManager (applies to all components)
2. Per-component middleware registered via @component decorator
3. Execution order: global middleware first, then per-component middleware
4. Priority ordering within each group (global, per-component)
5. Both class and function components with middleware
6. Imperative register_component() as alternative to decorator

This is the most complete example showing all middleware features working together.
"""

from dataclasses import dataclass
from typing import Any, Callable, cast

import svcs

from tdom_svcs.services.middleware import (
    Context,
    Middleware,
    MiddlewareManager,
    component,
    get_component_middleware,
    register_component,
    setup_container,
)
from tdom_svcs.types import Component


# Define global middleware (applies to all components)
@dataclass
class GlobalLoggingMiddleware:
    """Global logging middleware that runs for all components."""

    priority: int = -10  # Run early

    def __call__(
        self,
        component: Component,
        props: dict[str, Any],
        context: Context,
    ) -> dict[str, Any] | None:
        """Log all component processing."""
        name = component.__name__ if hasattr(component, "__name__") else str(component)
        print(f"  [GLOBAL-LOG] Processing {name}")
        return props


@dataclass
class GlobalValidationMiddleware:
    """Global validation middleware that runs for all components."""

    priority: int = 0  # Default priority

    def __call__(
        self,
        component: Component,
        props: dict[str, Any],
        context: Context,
    ) -> dict[str, Any] | None:
        """Validate common props."""
        print(f"  [GLOBAL-VALIDATE] Checking props...")

        # All components should have some props
        if not props:
            print(f"  [GLOBAL-VALIDATE] Error: No props provided")
            return None

        print(f"  [GLOBAL-VALIDATE] Props valid")
        return props


@dataclass
class GlobalTimestampMiddleware:
    """Global middleware that adds timestamp to all components."""

    priority: int = 10  # Run late

    def __call__(
        self,
        component: Component,
        props: dict[str, Any],
        context: Context,
    ) -> dict[str, Any] | None:
        """Add timestamp to props."""
        from datetime import datetime

        props["_rendered_at"] = datetime.now().isoformat()
        print(f"  [GLOBAL-TIMESTAMP] Added timestamp")
        return props


# Define per-component middleware (applies to specific components)
@dataclass
class ButtonSpecificMiddleware:
    """Middleware specific to Button components."""

    priority: int = -5  # Run early in per-component phase

    def __call__(
        self,
        component: Component,
        props: dict[str, Any],
        context: Context,
    ) -> dict[str, Any] | None:
        """Add button-specific defaults."""
        print(f"    [BUTTON-SPECIFIC] Adding button defaults")
        if "variant" not in props:
            props["variant"] = "primary"
        return props


@dataclass
class ButtonValidationMiddleware:
    """Validation middleware specific to Button components."""

    priority: int = 5  # Run late in per-component phase

    def __call__(
        self,
        component: Component,
        props: dict[str, Any],
        context: Context,
    ) -> dict[str, Any] | None:
        """Validate button-specific requirements."""
        print(f"    [BUTTON-VALIDATE] Checking button requirements")
        if "title" not in props:
            print(f"    [BUTTON-VALIDATE] Error: Button requires 'title' prop")
            return None
        print(f"    [BUTTON-VALIDATE] Button props valid")
        return props


@dataclass
class CardEnrichmentMiddleware:
    """Middleware specific to Card components."""

    priority: int = 0  # Default priority in per-component phase

    def __call__(
        self,
        component: Component,
        props: dict[str, Any],
        context: Context,
    ) -> dict[str, Any] | None:
        """Enrich card with additional data."""
        print(f"    [CARD-ENRICH] Adding card metadata")
        props["_card_type"] = "standard"
        return props


# Define components with per-component middleware

# Class component with decorator syntax
@component(
    middleware={
        "pre_resolution": [
            ButtonSpecificMiddleware(),
            ButtonValidationMiddleware(),
        ]
    }
)
@dataclass
class Button:
    """Button component with per-component middleware via decorator."""

    title: str = ""
    variant: str = "default"

    def __post_init__(self):
        print(f"      [BUTTON] Created: {self.title} ({self.variant})")


# Class component without decorator (will use imperative registration)
@dataclass
class Card:
    """Card component with per-component middleware via imperative registration."""

    title: str
    content: str = ""

    def __post_init__(self):
        print(f"      [CARD] Created: {self.title}")


# Function component without decorator (will use imperative registration)
def Heading(text: str, level: int = 1) -> str:
    """Heading function component with per-component middleware."""
    print(f"      [HEADING] Rendering level {level}: {text}")
    return f"<h{level}>{text}</h{level}>"


# Function component without decorator (will use imperative registration)
def Paragraph(text: str) -> str:
    """Paragraph function component."""
    print(f"      [PARAGRAPH] Rendering: {text[:30]}...")
    return f"<p>{text}</p>"


def simulate_middleware_execution(
    component: Component,
    props: dict[str, Any],
    manager: MiddlewareManager,
    context: Context,
) -> dict[str, Any] | None:
    """
    Simulate middleware execution with global + per-component middleware.

    In the real implementation, this happens inside the processor/hook system.
    Here we demonstrate it explicitly for educational purposes.
    """
    component_name = (
        component.__name__ if hasattr(component, "__name__") else str(component)
    )
    print(f"\n--- Processing {component_name} ---")

    # Phase 1: Execute global middleware (from MiddlewareManager)
    print(f"Phase 1: Global middleware (via MiddlewareManager)")
    result = manager.execute(component, props, context)
    if result is None:
        print(f"HALTED by global middleware\n")
        return None
    props = result

    # Phase 2: Execute per-component middleware
    print(f"Phase 2: Per-component middleware (via @component decorator)")
    component_middleware = get_component_middleware(component)

    if "pre_resolution" in component_middleware:
        # Sort by priority (lower first)
        middleware_list = sorted(
            component_middleware["pre_resolution"], key=lambda m: m.priority
        )

        for mw in middleware_list:
            result = mw(component, props, context)
            if result is None:
                print(f"HALTED by per-component middleware\n")
                return None
            # In this example, all middleware is synchronous
            props = cast(dict[str, Any], result)
    else:
        print(f"    (no per-component middleware)")

    print(f"SUCCESS: All middleware passed")
    return props


def main():
    """Demonstrate global and per-component middleware execution."""
    print("=" * 70)
    print("Global and Per-Component Middleware Example")
    print("=" * 70)

    # Setup: Create registry and context
    registry = svcs.Registry()
    context: Context = cast(Context, {"config": {"debug": True}})

    # Setup container (registers MiddlewareManager as service)
    setup_container(context, registry)
    container = svcs.Container(registry)
    manager = container.get(MiddlewareManager)

    # Register global middleware (applies to all components)
    print("\n" + "=" * 70)
    print("SETUP: Registering Global Middleware")
    print("=" * 70)
    manager.register_middleware(GlobalLoggingMiddleware())
    manager.register_middleware(GlobalValidationMiddleware())
    manager.register_middleware(GlobalTimestampMiddleware())
    print("Registered global middleware:")
    print("  - GlobalLoggingMiddleware (priority: -10)")
    print("  - GlobalValidationMiddleware (priority: 0)")
    print("  - GlobalTimestampMiddleware (priority: 10)")

    # Register per-component middleware imperatively for Card, Heading, and Paragraph
    print("\n" + "=" * 70)
    print("SETUP: Registering Per-Component Middleware")
    print("=" * 70)
    print("Via @component decorator:")
    print("  - Button: ButtonSpecificMiddleware, ButtonValidationMiddleware")
    print("\nVia imperative register_component():")

    # Register Card with per-component middleware
    register_component(
        Card,
        middleware={
            "pre_resolution": [
                CardEnrichmentMiddleware(),
            ]
        },
    )
    print("  - Card: CardEnrichmentMiddleware")

    # Register Heading with per-component middleware
    register_component(
        Heading,
        middleware={
            "pre_resolution": [
                GlobalLoggingMiddleware(priority=-5),  # Override priority for this component
            ]
        },
    )
    print("  - Heading: GlobalLoggingMiddleware (custom priority)")

    # Register Paragraph with per-component middleware
    register_component(
        Paragraph,
        middleware={
            "pre_resolution": [
                GlobalTimestampMiddleware(priority=-8),  # Custom priority
            ]
        },
    )
    print("  - Paragraph: GlobalTimestampMiddleware (custom priority)")

    # Execute middleware for different components
    print("\n" + "=" * 70)
    print("EXECUTION: Processing Components")
    print("=" * 70)

    # Test 1: Button with valid props (class component, decorator)
    print("\n" + "=" * 70)
    print("Test 1: Button with valid props")
    print("=" * 70)
    props = {"title": "Click Me"}
    result = simulate_middleware_execution(Button, props, manager, context)
    if result:
        print(f"Final props: {result}")
        # In real app, would instantiate: Button(**result)

    # Test 2: Button with missing title (class component, should fail validation)
    print("\n" + "=" * 70)
    print("Test 2: Button with missing title")
    print("=" * 70)
    props = {"variant": "secondary"}
    result = simulate_middleware_execution(Button, props, manager, context)
    if result:
        print(f"Final props: {result}")

    # Test 3: Card component (class component, imperative)
    print("\n" + "=" * 70)
    print("Test 3: Card component")
    print("=" * 70)
    props = {"title": "Welcome", "content": "Hello World"}
    result = simulate_middleware_execution(Card, props, manager, context)
    if result:
        print(f"Final props: {result}")

    # Test 4: Heading component (function component, decorator)
    print("\n" + "=" * 70)
    print("Test 4: Heading function component")
    print("=" * 70)
    props = {"text": "Welcome", "level": 2}
    result = simulate_middleware_execution(Heading, props, manager, context)
    if result:
        print(f"Final props: {result}")

    # Test 5: Paragraph component (function component, imperative)
    print("\n" + "=" * 70)
    print("Test 5: Paragraph function component")
    print("=" * 70)
    props = {"text": "This is a paragraph with some longer text content"}
    result = simulate_middleware_execution(Paragraph, props, manager, context)
    if result:
        print(f"Final props: {result}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY: Key Concepts Demonstrated")
    print("=" * 70)
    print("""
1. GLOBAL MIDDLEWARE (via MiddlewareManager)
   - Registered once, applies to all components
   - Executes first in priority order (-10, 0, 10)
   - Examples: logging, validation, timestamp

2. PER-COMPONENT MIDDLEWARE (via @component decorator)
   - Registered per component, only applies to that component
   - Executes after global middleware
   - Also respects priority ordering within per-component group
   - Can be registered via decorator or imperative function

3. EXECUTION ORDER
   Global (-10) -> Global (0) -> Global (10) ->
   PerComponent (-5) -> PerComponent (0) -> PerComponent (5)

4. BOTH CLASS AND FUNCTION COMPONENTS
   - Works with dataclass components (Button, Card)
   - Works with function components (Heading, Paragraph)
   - Middleware detects type via isinstance(component, type)

5. TWO REGISTRATION PATTERNS
   - Decorator: @component(middleware={...})
   - Imperative: register_component(component, middleware={...})

6. HALT BEHAVIOR
   - Any middleware can return None to halt execution
   - Useful for validation that prevents rendering
   - Example: ButtonValidationMiddleware halts on missing title
""")

    print("=" * 70)
    print("Example Complete")
    print("=" * 70)


if __name__ == "__main__":
    main()
