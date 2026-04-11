"""Middleware for the aria verifier example.

Demonstrates:
- Per-target middleware (not global) via @hookable decorator
- Middleware that inspects rendered output for accessibility issues
- Parsing rendered HTML strings to check for accessibility issues
- Dependency injection with Inject[Logger]

Uses @injectable for DI resolution (not @middleware - this is per-target).
"""

from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Any

from svcs_di import Inject
from svcs_hopscotch.injectors import injectable
from svcs_hopscotch.middleware import Props, PropsResult, Target
from markupsafe import Markup

from examples.middleware.aria.services import Logger


class _ImgAltChecker(HTMLParser):
    """HTML parser that collects img tags missing alt attributes."""

    def __init__(self) -> None:
        super().__init__()
        self.missing_alt: list[dict[str, str | None]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "img":
            attr_dict = dict(attrs)
            if "alt" not in attr_dict:
                self.missing_alt.append(attr_dict)


# The aria verifier middleware
@injectable
@dataclass
class AriaVerifierMiddleware:
    """Middleware that warns about accessibility issues.

    Renders the component and inspects the rendered HTML string for img
    tags missing alt attributes. Uses injected Logger service for warnings.
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
        """Render the target to get its HTML output."""
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
        """Check all img tags for alt attributes."""
        checker = _ImgAltChecker()
        checker.feed(str(node))
        for img_attrs in checker.missing_alt:
            src = img_attrs.get("src", "<unknown>")
            self.logger.warn(f"{target_name}: img src='{src}' missing alt attribute")
