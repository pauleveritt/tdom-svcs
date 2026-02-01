"""Head component with colocated CSS and JavaScript assets."""

from dataclasses import dataclass

from svcs_di.injectors import injectable
from tdom import Node

from tdom_svcs import html


@injectable
@dataclass
class Head:
    """Head component that references colocated static assets.

    The Head component demonstrates the colocated asset pattern:
    - head/ is a package containing the component
    - head/static/styles.css contains component CSS
    - head/static/script.js contains component JavaScript

    During authoring, relative paths (./static/...) work with IDE tooling.
    The PathCollector tracks these assets for build-time processing.
    """

    def __call__(self) -> Node:
        """Render head element with stylesheet and script references."""
        return html(
            t"""
            <head>
                <meta charset="utf-8">
                <title>Path Middleware Example</title>
                <link rel="stylesheet" href="./static/styles.css">
                <script src="./static/script.js"></script>
            </head>
        """
        )
