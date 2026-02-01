"""Middleware for the aria verifier example.

Demonstrates:
- Per-component middleware (not global) via @component decorator
- Middleware that inspects rendered output for accessibility issues
- Using aria-testing to query the Node tree
- Dependency injection with Inject[Logger]

Uses @injectable for DI resolution (not @middleware - this is per-component).
"""

from dataclasses import dataclass

from aria_testing import query_all_by_tag_name
from svcs_di import Inject
from svcs_di.injectors import injectable
from tdom import Node

from examples.middleware.aria.services import Logger
from tdom_svcs.types import Component, Context, Props, PropsResult


# The aria verifier middleware
@injectable
@dataclass
class AriaVerifierMiddleware:
    """Middleware that warns about accessibility issues.

    Renders the component and inspects the Node tree for img tags
    missing alt attributes. Uses injected Logger service for warnings.
    """

    logger: Inject[Logger]
    priority: int = 10

    def __call__(
        self, component: Component, props: Props, context: Context
    ) -> PropsResult:
        component_name = getattr(component, "__name__", type(component).__name__)

        # Render the component to inspect its output
        node = self._render_component(component)
        if node is not None:
            self._check_images(node, component_name)

        return props

    def _render_component(self, component: Component) -> Node | None:
        """Render the component to get its Node output."""
        try:
            # For dataclass components, instantiate then call
            if isinstance(component, type):
                instance = component()
                return instance()
            # For function components, just call
            return component()
        except Exception:
            # If rendering fails, skip inspection
            return None

    def _check_images(self, node: Node, component_name: str) -> None:
        """Check all img tags for alt attributes."""
        # Use aria-testing to find all img elements
        images = query_all_by_tag_name(node, "img")

        for img in images:
            if "alt" not in img.attrs:
                self.logger.warn(f"{component_name}: img missing alt attribute")
