"""Middleware for the aria verifier example.

Demonstrates:
- Per-target middleware (not global) via @hookable decorator
- Middleware that inspects rendered output for accessibility issues
- Using aria-testing to query the Node tree
- Dependency injection with Inject[Logger]

Uses @injectable for DI resolution (not @middleware - this is per-target).
"""

from dataclasses import dataclass
from typing import Any

from svcs_di import Inject
from svcs_hopscotch.injectors import injectable
from svcs_hopscotch.middleware import Props, PropsResult, Target
from markupsafe import Markup

from examples.middleware.aria.services import Logger


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

    def __call__(self, target: Target, props: Props, context: Any) -> PropsResult:
        target_name = getattr(target, "__name__", type(target).__name__)

        # Render the target to inspect its output
        node = self._render_target(target)
        if node is not None:
            self._check_images(node, target_name)

        return props

    def _render_target(self, target: Target) -> str | Markup | None:
        """Render the target to get its Node output."""
        try:
            # For dataclass targets, instantiate then call
            if isinstance(target, type):
                instance = target()
                return instance()
            # For function targets, just call
            return target()
        except Exception:
            # If rendering fails, skip inspection
            return None

    def _check_images(self, node: str | Markup, target_name: str) -> None:
        """Check all img tags for alt attributes.

        NOTE: String-based image inspection is a stub (roadmap item 18).
        The full Node-tree inspection using aria-testing will be restored
        in roadmap item 20 when rendering returns DOM objects again.
        """
        # TODO(item 20): restore query_all_by_tag_name(node, "img") check
        _ = node, target_name
