"""Focused unit tests for the two processor helpers."""

from dataclasses import dataclass
from string.templatelib import Template

import pytest
from svcs_di import Inject
from svcs_hopscotch.injectors import HopscotchContainer, HopscotchRegistry

from tdom_svcs.processor import (
    DIComponentProcessor,
    _get_implementation,
    needs_dependency_injection,
)

from .conftest import DatabaseService


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


def test_get_impl_none_container():
    class Base:
        pass

    assert _get_implementation(None, Base) is Base


def test_get_impl_no_override(empty_container):
    class Base:
        pass

    assert _get_implementation(empty_container, Base) is Base


def test_get_impl_registered_override(container_with_override):
    container, Base, Override = container_with_override
    assert _get_implementation(container, Base) is Override


# --- DIComponentProcessor._invoke_component ---


def test_invoke_plain_callable_no_container():
    proc = DIComponentProcessor()
    called_with: dict = {}

    def f(x: int = 1) -> Template:
        called_with["x"] = x
        return t"<p>{x}</p>"

    result = proc._invoke_component(None, f, {"x": 42})
    assert called_with["x"] == 42
    assert isinstance(result, Template)


def test_invoke_di_callable_with_container():
    """_invoke_component returns the DI-constructed instance (factory result, not Template)."""
    proc = DIComponentProcessor()

    @dataclass
    class C:
        db: Inject[DatabaseService]

        def __call__(self) -> Template:
            return t"<p>{self.db.get_user()}</p>"

    registry = HopscotchRegistry()
    registry.register_value(DatabaseService, DatabaseService())
    with HopscotchContainer(registry) as container:
        result = proc._invoke_component(container, C, {})

    assert isinstance(result, C)
    assert isinstance(result(), Template)


def test_invoke_di_callable_no_container_raises():
    proc = DIComponentProcessor()

    @dataclass
    class C:
        db: Inject[DatabaseService]

        def __call__(self) -> Template:
            return t"<p>{self.db.get_user()}</p>"

    with pytest.raises(TypeError, match="db"):
        proc._invoke_component(None, C, {})


def test_invoke_missing_required_param_raises():
    proc = DIComponentProcessor()

    def f(x: int) -> Template:
        return t"<p>{x}</p>"

    with pytest.raises(TypeError, match="x"):
        proc._invoke_component(None, f, {})
