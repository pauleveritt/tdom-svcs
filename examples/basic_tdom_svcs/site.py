"""Example-specific demonstration: Function components with KeywordInjector."""

from svcs_di.injectors.keyword import KeywordInjector

from basic_tdom_svcs.app import setup_application
from basic_tdom_svcs.components.button import button
from basic_tdom_svcs.components.greeting import greeting


def demonstrate_function_components(container):
    """
    Demonstrate function components with direct injection.

    This shows how function components work with KeywordInjector:
    1. Get the injector from the container
    2. Call injector(function) to get an instance with dependencies injected
    3. Call the returned instance with regular parameters

    Args:
        container: The svcs container with services registered
    """
    print("\n--- Function Component Demonstration ---\n")

    # Get the KeywordInjector from the container
    injector = container.get(KeywordInjector)

    # Inject dependencies into button function
    # The injector provides the 'db' parameter automatically
    button_with_deps = injector(button)

    # Call with regular parameters (label)
    # The 'db' parameter is already injected
    result1 = button_with_deps(label="Click Me")
    print(f"Button output: {result1}")

    # Inject dependencies into greeting function
    greeting_with_deps = injector(greeting)

    # Call with different user IDs
    result2 = greeting_with_deps(user_id=1)
    result3 = greeting_with_deps(user_id=2)
    result4 = greeting_with_deps(user_id=999)  # Unknown user

    print(f"Greeting 1: {result2}")
    print(f"Greeting 2: {result3}")
    print(f"Greeting 3: {result4}")

    print("\n✓ Function components work!")
    print("✓ Dependencies injected automatically via Inject[]")


def demonstrate_limitations():
    """
    Demonstrate what function components CANNOT do.

    Function components have limitations compared to class components:
    - Cannot be registered by string name
    - Cannot use @injectable decorator
    - Cannot be discovered via scan_components()
    - Cannot use ComponentLookup for resolution
    """
    print("\n--- Function Component Limitations ---\n")

    print("❌ Cannot register function by name:")
    print("   ComponentNameRegistry.register('Button', button)  # TypeError!")
    print()
    print("❌ Cannot use @injectable decorator:")
    print("   @injectable  # Only works on classes!")
    print("   def button(...): ...")
    print()
    print("❌ Cannot use ComponentLookup:")
    print("   lookup('Button', context)  # Won't find function components")
    print()
    print("✅ For these features, use class components with @injectable")
    print("   See: examples/basic_tdom_injectable")


def main():
    """Run the example."""
    print("=" * 60)
    print("Example: Basic tdom-svcs (Function Components)")
    print("=" * 60)
    print()
    print("This example shows the SIMPLEST use of dependency injection")
    print("with function components. This is for EDUCATIONAL purposes.")
    print()
    print("For PRODUCTION use, see: examples/basic_tdom_injectable")
    print("=" * 60)

    # Setup application
    registry, container = setup_application()

    # Demonstrate function components
    demonstrate_function_components(container)

    # Show limitations
    demonstrate_limitations()

    print("\n" + "=" * 60)
    print("Example complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
