"""Tests for register_implementation() component override feature."""

from dataclasses import dataclass

from markupsafe import Markup
from svcs_di import Inject
from svcs_di.injectors import HopscotchContainer, HopscotchRegistry

from tdom_svcs import html
from tdom_svcs.processor import _get_implementation

from .conftest import DatabaseService


@dataclass
class Greeting:
    """Base greeting component."""

    db: Inject[DatabaseService]

    def __call__(self) -> Markup:
        user = self.db.get_user()
        return Markup(f"<h1>Hello {user}!</h1>")


@dataclass
class FrenchGreeting(Greeting):
    """French greeting that overrides Greeting."""

    def __call__(self) -> Markup:
        user = self.db.get_user()
        return Markup(f"<h1>Bonjour {user}!</h1>")


@dataclass
class SpanishGreeting(Greeting):
    """Spanish greeting that overrides Greeting."""

    def __call__(self) -> Markup:
        user = self.db.get_user()
        return Markup(f"<h1>Hola {user}!</h1>")


def test_get_implementation_returns_registered_impl():
    """Test _get_implementation returns the registered implementation."""
    registry = HopscotchRegistry()
    registry.register_value(DatabaseService, DatabaseService())
    registry.register_implementation(Greeting, FrenchGreeting)

    with HopscotchContainer(registry) as container:
        impl = _get_implementation(container, Greeting)
        assert impl is FrenchGreeting


def test_get_implementation_returns_original_when_no_override():
    """Test _get_implementation returns original class when no override registered."""
    registry = HopscotchRegistry()
    registry.register_value(DatabaseService, DatabaseService())

    with HopscotchContainer(registry) as container:
        impl = _get_implementation(container, Greeting)
        assert impl is Greeting


def test_get_implementation_returns_original_for_non_container():
    """Test _get_implementation returns original class for non-DI contexts."""
    impl = _get_implementation({"not": "a container"}, Greeting)
    assert impl is Greeting

    impl = _get_implementation(None, Greeting)
    assert impl is Greeting


def test_template_uses_registered_implementation():
    """Test that templates use the registered implementation."""
    registry = HopscotchRegistry()
    registry.register_value(DatabaseService, DatabaseService())
    registry.register_implementation(Greeting, FrenchGreeting)

    with HopscotchContainer(registry) as container:
        result = html(t"<{Greeting} />", context=container)

    assert "Bonjour Alice!" in str(result)
    assert "Hello" not in str(result)


def test_template_uses_original_when_no_override():
    """Test that templates use original component when no override registered."""
    registry = HopscotchRegistry()
    registry.register_value(DatabaseService, DatabaseService())

    with HopscotchContainer(registry) as container:
        result = html(t"<{Greeting} />", context=container)

    assert "Hello Alice!" in str(result)


def test_override_can_be_changed():
    """Test that override can be changed by registering a different implementation."""
    registry = HopscotchRegistry()
    registry.register_value(DatabaseService, DatabaseService())

    # First register French
    registry.register_implementation(Greeting, FrenchGreeting)

    with HopscotchContainer(registry) as container:
        result = html(t"<{Greeting} />", context=container)
        assert "Bonjour" in str(result)

    # Now register Spanish (overwrites previous)
    registry.register_implementation(Greeting, SpanishGreeting)

    with HopscotchContainer(registry) as container:
        result = html(t"<{Greeting} />", context=container)
        assert "Hola" in str(result)


def test_multiple_components_with_different_overrides():
    """Test that different components can have different overrides."""

    @dataclass
    class Button:
        label: str = "Click"

        def __call__(self) -> Markup:
            return Markup(f"<button>{self.label}</button>")

    @dataclass
    class FrenchButton(Button):
        def __call__(self) -> Markup:
            return Markup(f"<button>Cliquez: {self.label}</button>")

    registry = HopscotchRegistry()
    registry.register_value(DatabaseService, DatabaseService())
    registry.register_implementation(Greeting, FrenchGreeting)
    registry.register_implementation(Button, FrenchButton)

    with HopscotchContainer(registry) as container:
        result = html(
            t"<div><{Greeting} /><{Button} label='OK' /></div>",
            context=container,
        )

    html_str = str(result)
    assert "Bonjour Alice!" in html_str
    assert "Cliquez: OK" in html_str


def test_override_inherits_di_fields():
    """Test that override implementation correctly inherits DI fields."""
    registry = HopscotchRegistry()
    db = DatabaseService()
    registry.register_value(DatabaseService, db)
    registry.register_implementation(Greeting, FrenchGreeting)

    with HopscotchContainer(registry) as container:
        result = html(t"<{Greeting} />", context=container)

    # The FrenchGreeting should have received the db via DI
    assert "Alice" in str(result)
