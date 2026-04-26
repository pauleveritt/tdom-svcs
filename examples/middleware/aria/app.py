"""Aria verifier middleware example.

Demonstrates:
- Per-target middleware that checks for accessibility issues
- Using aria-testing to inspect rendered Node trees
- Dependency injection for logging service

This example uses Hopscotch patterns (decorators, scanning) for convenience.
You can also use imperative registration if preferred.
"""

from svcs_hopscotch.injectors import HopscotchContainer, HopscotchRegistry

from examples.middleware.aria import components, middleware, services
from examples.middleware.aria.components import ImageWithAlt, ImageWithoutAlt
from examples.middleware.aria.services import Logger
from tdom_svcs import execute_target_middleware, html, scan


def main() -> str:
    """Execute middleware chain and verify accessibility warnings."""
    # Create registry and scan for @injectable and @hookable
    registry = HopscotchRegistry()
    scan(registry, middleware, components, services)

    with HopscotchContainer(registry) as container:
        # Get logger service for checking warnings
        logger = container.get(Logger)

        # Test: Target with alt (no warning)
        result = execute_target_middleware(ImageWithAlt, {}, container, "rendering")
        assert result is not None
        assert len(logger.warnings) == 0

        # Test: Target without alt (warning logged)
        result = execute_target_middleware(ImageWithoutAlt, {}, container, "rendering")
        assert result is not None
        assert len(logger.warnings) == 1
        assert "missing alt" in logger.warnings[0]

        # Render target
        response = html(t"<{ImageWithAlt} />", container=container)
        return str(response)


if __name__ == "__main__":
    print(main())
