"""Example demonstration: Multiple component patterns."""

from component_discovery.app import setup_application
from tdom_svcs.services.component_lookup import ComponentLookup


def demonstrate_components(container):
    """Demonstrate different component patterns."""
    print("\n--- Component Discovery Examples ---\n")

    lookup = container.get(ComponentLookup)

    # Component with no dependencies
    print("1. Button (no dependencies):")
    button = lookup("Button", context={"label": "Submit", "disabled": False})
    print(f"   {button()}\n")

    # Component with one dependency
    print("2. UserProfile (single dependency):")
    profile = lookup("UserProfile", context={"user_id": 2})
    print(f"   {profile()}\n")

    # Component with multiple dependencies
    print("3. AdminPanel (multiple dependencies):")
    panel = lookup("AdminPanel", context={"title": "System Dashboard"})
    print(f"   {panel()}\n")


def main():
    """Run the example."""
    print("=" * 60)
    print("Example: Component Discovery and Registration")
    print("=" * 60)

    registry, container = setup_application()
    demonstrate_components(container)

    print("\n✓ Example complete!")
    print("✓ All components discovered and resolved successfully")


if __name__ == "__main__":
    main()
