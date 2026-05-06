"""Components for the aria verifier example.

Demonstrates:
- Component with proper accessibility (alt attribute)
- Component missing accessibility (no alt attribute)
- Using @hookable decorator to attach per-target middleware
"""

from dataclasses import dataclass
from string.templatelib import Template

from examples.middleware.aria.middleware import AriaVerifierMiddleware
from tdom_svcs import hookable


# ImageWithAlt component with per-target middleware
# docs: start image-with-alt
@hookable(middleware={"rendering": [AriaVerifierMiddleware]})
@dataclass
class ImageWithAlt:
    """Component with proper alt attribute."""

    def __call__(self) -> Template:
        return t'<div><img src="photo.jpg" alt="A photo"></div>'


# docs: end image-with-alt


# docs: start image-without-alt
@hookable(middleware={"rendering": [AriaVerifierMiddleware]})
@dataclass
class ImageWithoutAlt:
    """Component missing alt attribute - will trigger warning."""

    def __call__(self) -> Template:
        return t'<div><img src="photo.jpg"></div>'


# docs: end image-without-alt
