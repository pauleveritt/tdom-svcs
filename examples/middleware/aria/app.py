"""Aria verifier middleware example.

Demonstrates:
- Per-component middleware that checks for accessibility issues
- Using aria-testing to inspect rendered Node trees
- Dependency injection for logging service

This example uses Hopscotch patterns (decorators, scanning) for convenience.
You can also use imperative registration if preferred.
"""

from svcs_di.injectors import HopscotchContainer, HopscotchRegistry

from examples.middleware.aria import components, middleware, services
from examples.middleware.aria.components import ImageWithAlt, ImageWithoutAlt
from examples.middleware.aria.services import Logger
from tdom_svcs import execute_component_middleware, html, scan


def main() -> str:
    """Execute middleware chain and verify accessibility warnings."""
    # Create registry and scan for @injectable and @component
    registry = HopscotchRegistry()
    scan(registry, middleware, components, services)

    with HopscotchContainer(registry) as container:
        # Get logger service for checking warnings
        logger = container.get(Logger)

        # Test: Component with alt (no warning)
        result = execute_component_middleware(ImageWithAlt, {}, container, "rendering")
        assert result is not None
        assert len(logger.warnings) == 0

        # Test: Component without alt (warning logged)
        result = execute_component_middleware(
            ImageWithoutAlt, {}, container, "rendering"
        )
        assert result is not None
        assert len(logger.warnings) == 1
        assert "missing alt" in logger.warnings[0]

        # Render component
        response = html(t"<{ImageWithAlt} />", context=container)
        return str(response)


if __name__ == "__main__":
    print(main())
