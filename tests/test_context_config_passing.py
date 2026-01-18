"""Tests for context and config parameter passing to components."""

from dataclasses import dataclass

from markupsafe import Markup
from svcs_di import HopscotchContainer, HopscotchRegistry, Inject

from tdom_svcs import html
from tdom_svcs.types import is_di_container

from .conftest import DatabaseService

# Test is_di_container helper


def testis_di_container_rejects_plain_dict():
    """Plain dict should not be considered a DI container."""
    d = {"foo": "bar"}
    assert not is_di_container(d)


def testis_di_container_accepts_hopscotch_container():
    """HopscotchContainer should be recognized as a DI container."""
    registry = HopscotchRegistry()
    with HopscotchContainer(registry) as container:
        assert is_di_container(container)


def testis_di_container_accepts_custom_container():
    """Custom class implementing DIContainer protocol should be recognized."""

    class MyContainer:
        def get(self, service_type: type):
            return service_type()

    container = MyContainer()
    assert is_di_container(container)


def testis_di_container_rejects_none():
    """None should not be a DI container."""
    assert not is_di_container(None)


# Test context passing to components


def test_function_component_receives_context():
    """Function component with context parameter receives it."""
    received_context = None

    def Greeting(name: str = "World", context=None):
        nonlocal received_context
        received_context = context
        return Markup(f"<p>Hello {name}</p>")

    ctx = {"user": "Alice"}
    result = html(t"<{Greeting} name='Test' />", context=ctx)

    assert str(result) == "<p>Hello Test</p>"
    assert received_context is ctx


def test_dataclass_component_receives_context():
    """Dataclass component's __call__ receives context."""
    received_context = None

    @dataclass
    class Greeting:
        name: str = "World"

        def __call__(self, context=None) -> Markup:
            nonlocal received_context
            received_context = context
            return Markup(f"<p>Hello {self.name}</p>")

    ctx = {"user": "Alice"}
    result = html(t"<{Greeting} name='Test' />", context=ctx)

    assert str(result) == "<p>Hello Test</p>"
    assert received_context is ctx


def test_component_receives_config():
    """Component with config parameter receives it."""
    received_config = None

    def Greeting(name: str = "World", config=None):
        nonlocal received_config
        received_config = config
        return Markup(f"<p>Hello {name}</p>")

    cfg = {"debug": True}
    result = html(t"<{Greeting} name='Test' />", config=cfg)

    assert str(result) == "<p>Hello Test</p>"
    assert received_config is cfg


def test_component_receives_context_and_config():
    """Component can receive both context and config."""
    received = {}

    def Greeting(name: str = "World", context=None, config=None):
        received["context"] = context
        received["config"] = config
        return Markup(f"<p>Hello {name}</p>")

    ctx = {"user": "Alice"}
    cfg = {"debug": True}
    result = html(t"<{Greeting} name='Test' />", context=ctx, config=cfg)

    assert str(result) == "<p>Hello Test</p>"
    assert received["context"] is ctx
    assert received["config"] is cfg


def test_component_without_context_param_ignores_it():
    """Component without context parameter works when context is provided."""

    def Greeting(name: str = "World"):
        return Markup(f"<p>Hello {name}</p>")

    ctx = {"user": "Alice"}
    result = html(t"<{Greeting} name='Test' />", context=ctx)

    assert str(result) == "<p>Hello Test</p>"


def test_dict_context_passed_but_no_di():
    """Plain dict context is passed to component but doesn't trigger DI."""
    received_context = None

    @dataclass
    class ComponentWithInject:
        db: Inject[DatabaseService]

        def __call__(self, context=None) -> Markup:
            nonlocal received_context
            received_context = context
            return Markup(f"<p>User: {self.db.get_user()}</p>")

    # With a plain dict, DI should NOT be triggered, so this should fail
    # because db is not injected
    ctx = {"user": "Alice"}
    try:
        html(t"<{ComponentWithInject} />", context=ctx)
        assert False, "Should have raised TypeError for missing db"
    except TypeError as e:
        assert "db" in str(e).lower()


def test_di_still_works_with_proper_container():
    """DI injection still works when proper container is provided."""
    received_context = None

    @dataclass
    class ComponentWithInject:
        db: Inject[DatabaseService]

        def __call__(self, context=None) -> Markup:
            nonlocal received_context
            received_context = context
            return Markup(f"<p>User: {self.db.get_user()}</p>")

    registry = HopscotchRegistry()
    db = DatabaseService()
    registry.register_value(DatabaseService, db)

    with HopscotchContainer(registry) as container:
        result = html(t"<{ComponentWithInject} />", context=container)

    assert str(result) == "<p>User: Alice</p>"
    # The container should be passed to __call__ as context
    assert received_context is container


def test_component_with_kwargs_receives_context():
    """Component with **kwargs receives context."""

    def Greeting(**kwargs):
        ctx = kwargs.get("context")
        name = kwargs.get("name", "World")
        return Markup(f"<p>Hello {name}, ctx={ctx is not None}</p>")

    ctx = {"user": "Alice"}
    result = html(t"<{Greeting} name='Test' />", context=ctx)

    assert str(result) == "<p>Hello Test, ctx=True</p>"


def test_nested_components_receive_context():
    """Nested components all receive the same context."""
    contexts_received = []

    def Outer(context=None, children=()):
        contexts_received.append(("outer", context))
        return Markup(f"<div>{''.join(str(c) for c in children)}</div>")

    def Inner(context=None):
        contexts_received.append(("inner", context))
        return Markup("<span>inner</span>")

    ctx = {"user": "Alice"}
    result = html(t"<{Outer}><{Inner} /></{Outer}>", context=ctx)

    assert str(result) == "<div><span>inner</span></div>"
    assert len(contexts_received) == 2
    # Children are resolved before being passed to parent
    assert contexts_received[0] == ("inner", ctx)
    assert contexts_received[1] == ("outer", ctx)


def test_di_component_call_receives_context_and_children():
    """DI component's __call__ receives both context and children."""
    received = {}

    @dataclass
    class Card:
        db: Inject[DatabaseService]
        title: str = "Card"

        def __call__(self, context=None, children: tuple = ()) -> Markup:
            received["context"] = context
            received["children"] = children
            user = self.db.get_user()
            children_html = "".join(str(child) for child in children)
            return Markup(f"<div>{self.title}: {user}{children_html}</div>")

    registry = HopscotchRegistry()
    db = DatabaseService()
    registry.register_value(DatabaseService, db)

    with HopscotchContainer(registry) as container:
        result = html(
            t"<{Card} title='Profile'><p>Child</p></{Card}>",
            context=container,
        )

    assert str(result) == "<div>Profile: Alice<p>Child</p></div>"
    assert received["context"] is container
    assert len(received["children"]) == 1


# Test function component DI injection


def test_function_component_with_inject():
    """Function component with Inject[] gets dependencies injected."""

    def Greeting(db: Inject[DatabaseService], name: str = "World") -> Markup:
        user = db.get_user()
        return Markup(f"<p>Hello {name}, user is {user}</p>")

    registry = HopscotchRegistry()
    registry.register_value(DatabaseService, DatabaseService())

    with HopscotchContainer(registry) as container:
        result = html(t"<{Greeting} name='Test' />", context=container)

    assert "Alice" in str(result)
    assert "Test" in str(result)


def test_function_component_with_multiple_inject():
    """Function component with multiple Inject[] parameters."""

    class CacheService:
        def get_cached(self) -> str:
            return "cached_value"

    def Component(db: Inject[DatabaseService], cache: Inject[CacheService]) -> Markup:
        return Markup(f"<p>DB: {db.get_user()}, Cache: {cache.get_cached()}</p>")

    registry = HopscotchRegistry()
    registry.register_value(DatabaseService, DatabaseService())
    registry.register_value(CacheService, CacheService())

    with HopscotchContainer(registry) as container:
        result = html(t"<{Component} />", context=container)

    assert "Alice" in str(result)
    assert "cached_value" in str(result)


def test_function_component_inject_without_container_fails():
    """Function component with Inject[] fails without DI container."""

    def Greeting(db: Inject[DatabaseService]) -> Markup:
        return Markup(f"<p>{db.get_user()}</p>")

    # Without a container, should fail because db is not injected
    try:
        html(t"<{Greeting} />")
        assert False, "Should have raised TypeError for missing db"
    except TypeError as e:
        assert "db" in str(e).lower()


def test_function_component_inject_with_dict_context_fails():
    """Function component with Inject[] fails with plain dict context."""

    def Greeting(db: Inject[DatabaseService]) -> Markup:
        return Markup(f"<p>{db.get_user()}</p>")

    # Plain dict doesn't trigger DI
    try:
        html(t"<{Greeting} />", context={"user": "Alice"})
        assert False, "Should have raised TypeError for missing db"
    except TypeError as e:
        assert "db" in str(e).lower()
