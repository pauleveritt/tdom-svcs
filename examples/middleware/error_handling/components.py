"""Components for the error handling middleware example."""

from dataclasses import dataclass

from tdom import Node

from tdom_svcs import html


@dataclass
class FailingComponent:
    """A component that intentionally fails for error handling demos.

    Used to demonstrate how middleware can catch and handle exceptions.
    """

    should_fail: bool = False

    def __post_init__(self) -> None:
        if self.should_fail:
            raise ValueError("FailingComponent was configured to fail!")

    def __call__(self) -> Node:
        return html(t"<div>This should not render if should_fail=True</div>")
