"""Components for the aria verifier example.

Demonstrates:
- Component with proper accessibility (alt attribute)
- Component missing accessibility (no alt attribute)
- Using @hookable decorator to attach per-target middleware
"""

from dataclasses import dataclass

from markupsafe import Markup

from examples.middleware.aria.middleware import AriaVerifierMiddleware
from tdom_svcs import hookable, html


# ImageWithAlt component with per-target middleware
@hookable(middleware={"rendering": [AriaVerifierMiddleware]})
@dataclass
class ImageWithAlt:
    """Component with proper alt attribute."""

    def __call__(self) -> str | Markup:
        return html(t'<div><img src="photo.jpg" alt="A photo"></div>')


@hookable(middleware={"rendering": [AriaVerifierMiddleware]})
@dataclass
class ImageWithoutAlt:
    """Component missing alt attribute - will trigger warning."""

    def __call__(self) -> str | Markup:
        return html(t'<div><img src="photo.jpg"></div>')
