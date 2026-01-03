"""
Example: Global Component Override

This example demonstrates how to override a component globally by registering
it last in the ComponentNameRegistry. When the same component name is registered
multiple times, the last registration wins for all lookups.

Use this pattern when you want to:
- Provide a site-specific customization of a base component
- Override third-party components with your own implementation
- Switch between implementations globally (e.g., for different deployment environments)

This corresponds to the Global Override Pattern in the documentation.
"""

from dataclasses import dataclass

import svcs
from svcs_di import Inject
from svcs_di.injectors.decorators import injectable
from svcs_di.injectors.locator import HopscotchInjector

from tdom_svcs import ComponentNameRegistry, scan_components
from tdom_svcs.services.component_lookup import ComponentLookup


# Define services
class ThemeService:
    """Service providing theme colors for the site."""

    def get_brand_color(self) -> str:
        return "#007bff"  # Site brand color


# Define base component (could be from a third-party library)
@injectable
@dataclass
class Button:
    """Base button component without theming."""

    label: str = "Click"

    def __call__(self) -> str:
        """Render basic button."""
        return f"<button>{self.label}</button>"


# Define site-specific override that uses theme service
@injectable
@dataclass
class ThemedButton:
    """Site-specific button with theme service integration."""

    theme: Inject[ThemeService]  # Injected dependency
    label: str = "Click"         # Regular parameter

    def __call__(self) -> str:
        """Render themed button with brand color."""
        color = self.theme.get_brand_color()
        return f'<button style="color: {color}">{self.label}</button>'


def setup_application() -> tuple[svcs.Container, ComponentNameRegistry]:
    """Set up application with global component override."""
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()

    # Register services
    registry.register_value(ThemeService, ThemeService())

    # Discover components - both Button and ThemedButton are registered
    scan_components(registry, component_registry, __name__)

    # IMPORTANT: Override by registering the same name again
    # The last registration wins for global lookups
    print("\n1. Initial registration:")
    print(f"   Button type: {component_registry.get_type('Button')}")

    # Global override: register ThemedButton under the "Button" name
    component_registry.register("Button", ThemedButton)
    print("\n2. After global override:")
    print(f"   Button type: {component_registry.get_type('Button')}")
    print(f"   (Now points to ThemedButton)")

    # Setup infrastructure
    registry.register_value(ComponentNameRegistry, component_registry)
    registry.register_factory(HopscotchInjector, HopscotchInjector)

    def component_lookup_factory(container: svcs.Container) -> ComponentLookup:
        return ComponentLookup(container=container)

    registry.register_factory(ComponentLookup, component_lookup_factory)

    container = svcs.Container(registry)
    return container, component_registry


def demonstrate_global_override():
    """Demonstrate global component override."""
    print("=" * 70)
    print("Global Component Override Example")
    print("=" * 70)

    container, component_registry = setup_application()

    # Check registered components
    print("\n3. All registered components:")
    for name in sorted(component_registry.get_all_names()):
        component_type = component_registry.get_type(name)
        print(f"   - {name}: {component_type.__name__}")

    # Get ComponentLookup
    lookup = container.get(ComponentLookup)

    # Resolve "Button" - will use ThemedButton (the override)
    print("\n4. Resolving 'Button' component:")
    button = lookup("Button", context={"label": "Submit"})
    rendered = button()
    print(f"   Rendered: {rendered}")
    print(f"   (Notice the brand color is applied)")

    # The original Button class is still available as "ThemedButton"
    print("\n5. Original Button is still accessible:")
    print(f"   ThemedButton registered: {component_registry.get_type('ThemedButton') is not None}")

    print("\n" + "=" * 70)
    print("Key points about Global Override:")
    print("=" * 70)
    print("  1. Last registration wins for the same component name")
    print("  2. Override applies to all lookups of that name")
    print("  3. Original class is still available if registered under different name")
    print("  4. Useful for site-wide customization of base components")
    print("  5. Simple pattern - just register again with the same name")


if __name__ == "__main__":
    demonstrate_global_override()
