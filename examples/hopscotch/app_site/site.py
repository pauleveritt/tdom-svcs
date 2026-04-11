"""A site that configures an app."""

from svcs_hopscotch.hopscotch_registry import HopscotchRegistry


def svcs_registry(registry: HopscotchRegistry) -> None:
    """Called automatically during scan() - no site customizations."""
    pass
