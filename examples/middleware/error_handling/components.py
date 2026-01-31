"""Components for the error handling middleware example.

Re-exports common Greeting and adds FailingComponent for error demos.
"""

from tdom import Node

# Re-export common components
from examples.common.components import Greeting
from tdom_svcs import html

__all__ = ["FailingComponent", "Greeting"]


class FailingComponent:
    """A component that intentionally fails for error handling demos.

    Used to demonstrate how middleware can catch and handle exceptions.
    """

    def __init__(self, should_fail: bool = False, **kwargs):
        self.should_fail = should_fail
        if should_fail:
            raise ValueError("FailingComponent was configured to fail!")

    def __call__(self) -> Node:
        return html(t"<div>This should not render if should_fail=True</div>")
