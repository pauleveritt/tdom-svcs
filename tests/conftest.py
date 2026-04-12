"""Shared test fixtures for tdom-svcs tests."""

from collections.abc import Generator

import pytest
from svcs_hopscotch.injectors import HopscotchContainer, HopscotchRegistry


class DatabaseService:
    """Fake database service for testing DI."""

    def get_user(self) -> str:
        return "Alice"


class AuthService:
    """Fake auth service for testing DI."""

    def is_authenticated(self) -> bool:
        return True


@pytest.fixture
def registry() -> HopscotchRegistry:
    """Create a fresh HopscotchRegistry."""
    return HopscotchRegistry()


@pytest.fixture
def registry_with_db() -> HopscotchRegistry:
    """Create a HopscotchRegistry with DatabaseService pre-registered."""
    reg = HopscotchRegistry()
    reg.register_value(DatabaseService, DatabaseService())
    return reg


@pytest.fixture
def container(registry: HopscotchRegistry) -> Generator[HopscotchContainer]:
    """Create a HopscotchContainer from registry."""
    with HopscotchContainer(registry) as c:
        yield c


@pytest.fixture
def container_with_db(
    registry_with_db: HopscotchRegistry,
) -> Generator[HopscotchContainer]:
    """Create a HopscotchContainer with DatabaseService available."""
    with HopscotchContainer(registry_with_db) as c:
        yield c
