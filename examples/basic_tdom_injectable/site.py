"""Example-specific demonstration: Class components with ComponentLookup."""

from basic_tdom_injectable.app import setup_application
from tdom_svcs.services.component_lookup import ComponentLookup


def demonstrate_component_lookup(container):
    """
    Demonstrate component resolution via ComponentLookup.

    This shows the production pattern:
    1. Get ComponentLookup from container
    2. Resolve components by string name
    3. Components are automatically constructed with dependencies injected
    4. Call component to render

    Args:
        container: The svcs container with all services registered
    """
    print("\n--- Component Lookup Demonstration ---\n")

    # Get ComponentLookup service from container
    lookup = container.get(ComponentLookup)

    # Resolve components by string name
    # The string name comes from the class name (Button -> "Button")
    button = lookup("Button", context={"label": "Click Me"})
    print(f"✓ Resolved Button component: {button}")
    print(f"  Button output: {button()}\n")

    # Resolve UserCard with user_id parameter
    user_card = lookup("UserCard", context={"user_id": 2})
    print(f"✓ Resolved UserCard component: {user_card}")
    print(f"  UserCard output: {user_card()}\n")

    # Resolve Dashboard (no parameters needed, only injected dependencies)
    dashboard = lookup("Dashboard", context={})
    print(f"✓ Resolved Dashboard component: {dashboard}")
    print(f"  Dashboard output: {dashboard()}\n")


def demonstrate_direct_construction(container):
    """
    Demonstrate direct component construction (alternative pattern).

    You can also construct components directly if you don't need
    string name resolution. This is useful when you have the class
    reference available.

    Args:
        container: The svcs container
    """
    print("\n--- Direct Construction Demonstration ---\n")

    from svcs_di.injectors.locator import HopscotchInjector

    from basic_tdom_injectable.components.button import Button

    # Get injector
    injector = container.get(HopscotchInjector)

    # Construct directly with type reference
    button = injector(Button, label="Direct Button")
    print(f"✓ Directly constructed Button: {button}")
    print(f"  Output: {button()}\n")

    print("NOTE: Direct construction is fine when you have the class reference.")
    print("      Use ComponentLookup when resolving by string name (e.g., from templates).")


def demonstrate_automatic_injection(container):
    """
    Demonstrate how automatic dependency injection works.

    This shows that:
    - Services (db, auth) are automatically provided
    - You only supply regular parameters (label, user_id)
    - Dependencies are resolved from the container

    Args:
        container: The svcs container
    """
    print("\n--- Automatic Injection Demonstration ---\n")

    lookup = container.get(ComponentLookup)

    print("When you resolve a component:")
    print('  button = lookup("Button", context={"label": "Click"})')
    print()
    print("Behind the scenes:")
    print("  1. ComponentLookup gets Button type from ComponentNameRegistry")
    print("  2. HopscotchInjector constructs Button instance")
    print("  3. Injector sees: Button(label: str, db: Inject[DatabaseService])")
    print("  4. Injector provides 'db' from container automatically")
    print("  5. You only provided 'label' in context")
    print("  6. Result: Button(label='Click', db=<DatabaseService>)")
    print()

    button = lookup("Button", context={"label": "Example"})
    print(f"✓ Component created with automatic injection: {button}")
    print(f"  - label='Example' (from context)")
    print(f"  - db=<DatabaseService> (injected automatically)")


def main():
    """Run the example."""
    print("=" * 70)
    print("Example: Basic tdom-svcs with @injectable (Class Components)")
    print("=" * 70)
    print()
    print("This example shows the RECOMMENDED PRODUCTION PATTERN:")
    print("  - Class components with @injectable decorator")
    print("  - Automatic scanning with scan_components()")
    print("  - HopscotchInjector for production use")
    print("  - ComponentLookup for string name resolution")
    print("=" * 70)

    # Setup application (standard pattern)
    registry, container = setup_application()

    # Demonstrate component lookup (primary pattern)
    demonstrate_component_lookup(container)

    # Show alternative: direct construction
    demonstrate_direct_construction(container)

    # Explain how injection works
    demonstrate_automatic_injection(container)

    print("\n" + "=" * 70)
    print("Example complete!")
    print()
    print("Key Takeaways:")
    print("  ✓ Use @injectable on class components")
    print("  ✓ Use scan_components() at app startup")
    print("  ✓ Use HopscotchInjector for production")
    print("  ✓ Use ComponentLookup to resolve by string name")
    print("  ✓ Dependencies injected automatically via Inject[]")
    print("=" * 70)


if __name__ == "__main__":
    main()
