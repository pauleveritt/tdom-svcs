"""Components for the aria verifier example.

Demonstrates:
- Component with proper accessibility (alt attribute)
- Component missing accessibility (no alt attribute)
- Using @component decorator to attach per-component middleware
"""

from dataclasses import dataclass

from tdom import Node

from examples.middleware.aria.middleware import AriaVerifierMiddleware
from tdom_svcs import component, html


# ImageWithAlt component with per-component middleware
@component(middleware={"rendering": [AriaVerifierMiddleware]})
@dataclass
class ImageWithAlt:
    """Component with proper alt attribute."""

    def __call__(self) -> Node:
        return html(t'<div><img src="photo.jpg" alt="A photo"></div>')


@component(middleware={"rendering": [AriaVerifierMiddleware]})
@dataclass
class ImageWithoutAlt:
    """Component missing alt attribute - will trigger warning."""

    def __call__(self) -> Node:
        return html(t'<div><img src="photo.jpg"></div>')
