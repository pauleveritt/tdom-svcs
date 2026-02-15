from typing import Protocol, TypeGuard, TypeVar, runtime_checkable

# -------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------

COMPONENT_LOCATION_PROP = "_component_location"
"""Internal prop key for storing component location during rendering."""

# -------------------------------------------------------------------------
# Protocols
# -------------------------------------------------------------------------

T = TypeVar("T")


@runtime_checkable
class DIContainer(Protocol):
    """Protocol for dependency injection containers."""

    def get(self, service_type: type[T]) -> T:
        """Resolve and return an instance of the requested service type."""
        ...


def is_di_container(obj: object) -> TypeGuard[DIContainer]:
    """Check if obj is a proper DI container (excludes dicts)."""
    if isinstance(obj, dict):
        return False
    return isinstance(obj, DIContainer)
