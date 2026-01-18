"""Component discovery example.

Demonstrates resolving multiple components with different dependency patterns
using HopscotchContainer's inject() method.
"""

from svcs_di import HopscotchContainer, HopscotchRegistry

from examples.component_discovery import site
from examples.component_discovery.components import AdminPanel, Button, UserProfile


def main() -> str:
    """Resolve and render components with dependency injection."""
    registry = HopscotchRegistry()

    # Setup services from site.py
    site.svcs_setup(registry)

    # Register components
    registry.register_factory(Button, Button)
    registry.register_factory(UserProfile, UserProfile)
    registry.register_factory(AdminPanel, AdminPanel)

    with HopscotchContainer(registry) as container:
        # Resolve components - inject() handles Inject[] automatically
        button = container.inject(Button)  # ty: ignore[unresolved-attribute]
        profile = container.inject(UserProfile)  # ty: ignore[unresolved-attribute]
        panel = container.inject(AdminPanel)  # ty: ignore[unresolved-attribute]

        # Render and verify
        button_html = str(button())
        profile_html = str(profile())
        panel_html = str(panel())

        assert "<button>" in button_html
        assert "User:" in profile_html
        assert "Admin Panel" in panel_html

        return f"{button_html}\n{profile_html}\n{panel_html}"


if __name__ == "__main__":
    print(main())
