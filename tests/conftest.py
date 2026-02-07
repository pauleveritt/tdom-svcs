"""Shared test fixtures for tdom-svcs tests."""

import pytest
from svcs_di.injectors import HopscotchContainer, HopscotchRegistry


# =============================================================================
# Mock Services
# =============================================================================


class DatabaseService:
    """Mock database service for testing DI."""

    def get_user(self) -> str:
        return "Alice"


class AuthService:
    """Mock auth service for testing DI."""

    def is_authenticated(self) -> bool:
        return True


# =============================================================================
# Registry and Container Fixtures
# =============================================================================


@pytest.fixture
def registry() -> HopscotchRegistry:
    """Create a fresh HopscotchRegistry for testing."""
    return HopscotchRegistry()


@pytest.fixture
def container(registry: HopscotchRegistry):
    """Create a HopscotchContainer from registry."""
    with HopscotchContainer(registry) as container:
        yield container
