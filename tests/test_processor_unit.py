"""Focused unit tests for the two processor helpers."""

from dataclasses import dataclass

import pytest
from svcs_di import Inject
from svcs_hopscotch.injectors import HopscotchContainer, HopscotchRegistry
from tdom.processor import IComponentProcessor

from tdom_svcs.processor import (
    DIComponentProcessor,
    _get_implementation,
    needs_dependency_injection,
)

from .conftest import DatabaseService

# Protocol-satisfaction assertion: ty verifies DIComponentProcessor satisfies
# IComponentProcessor[None] (DefaultAppState) at type-check time.
_: IComponentProcessor[None] = DIComponentProcessor()


def _plain_function():
    return None


@dataclass
class _PlainDataclass:
    name: str = "x"


@dataclass
class _DIDataclass:
    db: Inject[DatabaseService]


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (_plain_function, False),
        (_PlainDataclass, False),
        (_DIDataclass, True),
        ("not callable", False),
        (42, False),
    ],
)
def test_needs_dependency_injection(value: object, expected: bool):
    assert needs_dependency_injection(value) is expected


@pytest.fixture
def empty_container():
    with HopscotchContainer(HopscotchRegistry()) as c:
        yield c


@pytest.fixture
def container_with_override():
    class Base:
        pass

    class Override(Base):
        pass

    registry = HopscotchRegistry()
    registry.register_implementation(Base, Override)
    with HopscotchContainer(registry) as c:
        yield c, Base, Override


def test_get_impl_no_locator(empty_container):
    """_get_implementation returns original cls when no locator is found."""

    class Base:
        pass

    assert _get_implementation(empty_container, Base) is Base


def test_get_impl_no_override(empty_container):
    class Base:
        pass

    assert _get_implementation(empty_container, Base) is Base


def test_get_impl_registered_override(container_with_override):
    container, Base, Override = container_with_override
    assert _get_implementation(container, Base) is Override
