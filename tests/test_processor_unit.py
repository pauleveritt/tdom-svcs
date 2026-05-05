"""Focused unit tests for the two processor helpers."""

from dataclasses import dataclass
from string.templatelib import Template
from typing import Protocol

import pytest
from svcs_di import Inject
from svcs_hopscotch.injectors import HopscotchContainer, HopscotchRegistry
from tdom.processor import IComponentProcessor

from tdom_svcs import html
from tdom_svcs.processor import (
    DIComponentProcessor,
    _get_implementation,
    _inspect_component_resolution,
    needs_dependency_injection,
)

from .conftest import DatabaseService

# Protocol-satisfaction assertion: ty verifies DIComponentProcessor satisfies
# tdom's non-generic IComponentProcessor protocol.
_: IComponentProcessor = DIComponentProcessor()


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


def test_inspect_component_resolution_for_native_tag(empty_container):
    decision = _inspect_component_resolution(empty_container, "div")

    assert decision.kind == "native-tag"
    assert decision.requested == "div"
    assert decision.final_callable is None
    assert decision.implementation_swapped is False


def test_inspect_component_resolution_for_plain_component(empty_container):
    decision = _inspect_component_resolution(empty_container, _PlainDataclass)

    assert decision.kind == "component"
    assert decision.requested is _PlainDataclass
    assert decision.final_callable is _PlainDataclass
    assert decision.implementation_swapped is False


def test_inspect_component_resolution_for_registered_override(container_with_override):
    container, Base, Override = container_with_override
    decision = _inspect_component_resolution(container, Base)

    assert decision.kind == "component"
    assert decision.requested is Base
    assert decision.final_callable is Override
    assert decision.implementation_swapped is True


def test_inspect_component_resolution_for_protocol_override_keeps_rendering():
    class IHeader(Protocol):
        def __call__(self) -> Template: ...

    @dataclass
    class Header:
        def __call__(self) -> Template:
            return t"<h1>Header</h1>"

    registry = HopscotchRegistry()
    registry.register_implementation(IHeader, Header)

    with HopscotchContainer(registry) as container:
        decision = _inspect_component_resolution(container, IHeader)
        rendered = html(t"<{IHeader} />", container=container)

    assert decision.kind == "component"
    assert decision.requested is IHeader
    assert decision.final_callable is Header
    assert decision.implementation_swapped is True
    assert rendered == "<h1>Header</h1>"
