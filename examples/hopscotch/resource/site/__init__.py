"""A site that configures an app."""

from svcs_hopscotch.hopscotch_registry import HopscotchRegistry
from svcs_hopscotch.injectors import scan

from examples.hopscotch.resource.site import components


def svcs_registry(registry: HopscotchRegistry) -> None:
    """Called automatically during scan() - registers site components."""
    scan(registry, components)
