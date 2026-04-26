"""Tests for context and config parameter passing to components."""

from dataclasses import dataclass

import pytest
from markupsafe import Markup
from svcs_di import Inject
from svcs_hopscotch.injectors import HopscotchContainer, HopscotchRegistry

from tdom_svcs import html

from .conftest import DatabaseService

# Test context passing to components


def test_function_component_receives_context():
    """Function component with context parameter receives None when no container is provided."""
    received_context = None

    def Greeting(name: str = "World", context=None):
        nonlocal received_context
        received_context = context
        return Markup(f"<p>Hello {name}</p>")

    result = html(t"<{Greeting} name='Test' />", container=None)

    assert str(result) == "<p>Hello Test</p>"
    assert received_context is None


def test_dataclass_component_receives_context():
    """Dataclass component's __call__ receives None when no container is provided."""
    received_context = None

    @dataclass
    class Greeting:
        name: str = "World"

        def __call__(self, context=None) -> str | Markup:
            nonlocal received_context
            received_context = context
            return Markup(f"<p>Hello {self.name}</p>")

    result = html(t"<{Greeting} name='Test' />", container=None)

    assert str(result) == "<p>Hello Test</p>"
    assert received_context is None


def test_component_receives_config_from_context():
    """Config comes from the container (registered as a service), not a separate param."""

    class AppConfig:
        debug = True

    received_config = None

    @dataclass
    class Greeting:
        config: Inject[AppConfig]
        name: str = "World"

        def __call__(self) -> str | Markup:
            nonlocal received_config
            received_config = self.config
            return Markup(f"<p>Hello {self.name}</p>")

    registry = HopscotchRegistry()
    cfg = AppConfig()
    registry.register_value(AppConfig, cfg)

    with HopscotchContainer(registry) as container:
        result = html(t"<{Greeting} name='Test' />", container=container)

    assert str(result) == "<p>Hello Test</p>"
    assert received_config is cfg


def test_component_without_context_param_ignores_it():
    """Component without context parameter works when container is None."""

    def Greeting(name: str = "World"):
        return Markup(f"<p>Hello {name}</p>")

    result = html(t"<{Greeting} name='Test' />", container=None)

    assert str(result) == "<p>Hello Test</p>"


def test_di_still_works_with_proper_container():
    """DI injection still works when proper container is provided."""
    received_context = None

    @dataclass
    class ComponentWithInject:
        db: Inject[DatabaseService]

        def __call__(self, context=None) -> str | Markup:
            nonlocal received_context
            received_context = context
            return Markup(f"<p>User: {self.db.get_user()}</p>")

    registry = HopscotchRegistry()
    db = DatabaseService()
    registry.register_value(DatabaseService, db)

    with HopscotchContainer(registry) as container:
        result = html(t"<{ComponentWithInject} />", container=container)

    assert str(result) == "<p>User: Alice</p>"
    # The container should be passed to __call__ as context
    assert received_context is container


def test_component_with_kwargs_receives_context():
    """Component with **kwargs receives context when container is None."""

    def Greeting(**kwargs):
        ctx = kwargs.get("context")
        name = kwargs.get("name", "World")
        return Markup(f"<p>Hello {name}, ctx={ctx is not None}</p>")

    result = html(t"<{Greeting} name='Test' />", container=None)

    assert str(result) == "<p>Hello Test, ctx=False</p>"


def test_nested_components_receive_context():
    """Nested components all receive the same context (None when no container)."""
    contexts_received = []

    def Outer(context=None, children=""):
        contexts_received.append(("outer", context))
        return Markup(f"<div>{children}</div>")

    def Inner(context=None):
        contexts_received.append(("inner", context))
        return Markup("<span>inner</span>")

    result = html(t"<{Outer}><{Inner} /></{Outer}>", container=None)

    assert str(result) == "<div><span>inner</span></div>"
    assert len(contexts_received) == 2
    # Children are resolved before being passed to parent
    assert contexts_received[0] == ("inner", None)
    assert contexts_received[1] == ("outer", None)


def test_di_component_call_receives_context_and_children():
    """DI component's __call__ receives both context and children."""
    received = {}

    @dataclass
    class Card:
        db: Inject[DatabaseService]
        title: str = "Card"

        def __call__(self, context=None, children: str | Markup = "") -> str | Markup:
            received["context"] = context
            received["children"] = children
            user = self.db.get_user()
            return Markup(f"<div>{self.title}: {user}{children}</div>")

    registry = HopscotchRegistry()
    db = DatabaseService()
    registry.register_value(DatabaseService, db)

    with HopscotchContainer(registry) as container:
        result = html(
            t"<{Card} title='Profile'><p>Child</p></{Card}>",
            container=container,
        )

    assert str(result) == "<div>Profile: Alice<p>Child</p></div>"
    assert received["context"] is container
    assert str(received["children"]) == "<p>Child</p>"


# Test function component DI injection


def test_function_component_with_inject():
    """Function component with Inject[] gets dependencies injected."""

    def Greeting(db: Inject[DatabaseService], name: str = "World") -> str | Markup:
        user = db.get_user()
        return Markup(f"<p>Hello {name}, user is {user}</p>")

    registry = HopscotchRegistry()
    registry.register_value(DatabaseService, DatabaseService())

    with HopscotchContainer(registry) as container:
        result = html(t"<{Greeting} name='Test' />", container=container)

    assert "Alice" in str(result)
    assert "Test" in str(result)


def test_function_component_with_multiple_inject():
    """Function component with multiple Inject[] parameters."""

    class CacheService:
        def get_cached(self) -> str:
            return "cached_value"

    def Component(
        db: Inject[DatabaseService], cache: Inject[CacheService]
    ) -> str | Markup:
        return Markup(f"<p>DB: {db.get_user()}, Cache: {cache.get_cached()}</p>")

    registry = HopscotchRegistry()
    registry.register_value(DatabaseService, DatabaseService())
    registry.register_value(CacheService, CacheService())

    with HopscotchContainer(registry) as container:
        result = html(t"<{Component} />", container=container)

    assert "Alice" in str(result)
    assert "cached_value" in str(result)


def test_function_component_inject_without_container_fails():
    """Function component with Inject[] fails without DI container."""

    def Greeting(db: Inject[DatabaseService]) -> str | Markup:
        return Markup(f"<p>{db.get_user()}</p>")

    # Without a container, should fail because db is not injected
    with pytest.raises(TypeError, match="db"):
        html(t"<{Greeting} />")
