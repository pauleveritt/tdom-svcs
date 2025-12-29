"""
Example: Direct Decorator Application

This example demonstrates using injectable() directly without decorator syntax.
This is useful for programmatic decoration, conditional registration, and
creating variants of components.

Note: When applying injectable() directly, the registered name is still the
original class name. Variants share the same string name but have different
resource metadata.
"""

from direct_decorator.app import setup_application


def demonstrate_direct_decorator_application():
    """Demonstrate direct decorator application patterns."""
    lookup, component_registry = setup_application()

    print("Direct Decorator Application Example")
    print("=" * 60)

    # Check what components were discovered
    print("\nDiscovered components:")
    for name in sorted(component_registry.get_all_names()):
        print(f"  - {name}")

    print("\n" + "=" * 60)

    context = {}

    # Example 4: Basic direct application
    print("\n1. Card (applied with injectable(Card)):")
    card = lookup("Card", context)
    if card:
        rendered = card()
        print(f"   {rendered}")

    # Example 5: Separate classes with different resource metadata
    print("\n2. CustomerDashboard (resource=CustomerContext):")
    customer_dash = lookup("CustomerDashboard", context)
    if customer_dash:
        rendered = customer_dash()
        print(f"   {rendered}")

    print("\n3. AdminDashboard (resource=AdminContext):")
    admin_dash = lookup("AdminDashboard", context)
    if admin_dash:
        rendered = admin_dash()
        print(f"   {rendered}")

    # Conditional decoration example
    print("\n4. AnalyticsWidget (conditionally decorated):")
    analytics = lookup("AnalyticsWidget", context)
    if analytics:
        rendered = analytics()
        print(f"   {rendered}")

    print("\n5. ReportingWidget (conditionally decorated - disabled):")
    try:
        reporting = lookup("ReportingWidget", context)
        if reporting:
            print("   (Should not be found)")
    except Exception as e:
        print(f"   Not found (as expected): {type(e).__name__}")

    print("\n" + "=" * 60)
    print("\nWhen to use direct application:")
    print("  1. Conditional decoration based on configuration")
    print("  2. Decorating classes from third-party libraries")
    print("  3. Applying different resource/location metadata to classes")
    print("  4. Dynamic component registration in plugins")
    print("  5. Testing scenarios requiring explicit control")
    print("\nKey points:")
    print("  1. injectable() can be called as a regular function")
    print("  2. Create separate classes for variants (CustomerDashboard, AdminDashboard)")
    print("  3. Apply injectable() with different resource metadata")
    print("  4. Each class registered by its own __name__")
    print("  5. Feature flags control which components are decorated")
    print("\nImportant:")
    print("  - Component name is always derived from class.__name__")
    print("  - To create variants, define separate classes")
    print("  - Resource/location metadata affects resolution, not naming")


if __name__ == "__main__":
    demonstrate_direct_decorator_application()
