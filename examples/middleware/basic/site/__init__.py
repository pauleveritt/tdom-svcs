"""A site that configures an app.

In more complex examples, this would scan site-specific overrides.
For the basic example, it serves as a placeholder showing the pattern.
"""

from svcs_di.hopscotch_registry import HopscotchRegistry


def svcs_registry(registry: HopscotchRegistry) -> None:
    """Called automatically during scan() - no site customizations."""
    pass
