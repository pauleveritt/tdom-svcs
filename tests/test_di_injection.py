"""Tests for DI injection mechanism."""

import threading
from dataclasses import dataclass

import pytest
from string.templatelib import Template
from svcs_di import Inject
from svcs_hopscotch.injectors import HopscotchContainer, HopscotchRegistry

from tdom_svcs import html
from tdom_svcs.processor import needs_dependency_injection

from .conftest import AuthService, DatabaseService

# Test components


@dataclass
class SimpleComponent:
    """Component without DI."""

    label: str = "Default"

    def __call__(self) -> Template:
        return t"<div>{self.label}</div>"


@dataclass
class ButtonWithDI:
    """Component with single DI dependency."""

    db: Inject[DatabaseService]
    label: str = "Click"

    def __call__(self) -> Template:
        user = self.db.get_user()
        return t"<button>Hello {user}: {self.label}</button>"


@dataclass
class ComplexComponent:
    """Component with multiple DI dependencies and regular params."""

    db: Inject[DatabaseService]
    auth: Inject[AuthService]
    title: str = "Dashboard"

    def __call__(self) -> Template:
        user = self.db.get_user()
        authenticated = "Yes" if self.auth.is_authenticated() else "No"
        return t"<div>{self.title}: User={user}, Auth={authenticated}</div>"


def test_needs_dependency_injection():
    """Test that needs_dependency_injection correctly identifies DI components."""
    assert not needs_dependency_injection(SimpleComponent)
    assert needs_dependency_injection(ButtonWithDI)
    assert needs_dependency_injection(ComplexComponent)

    # Functions can't have Inject fields
    def some_function():
        return "test"

    assert not needs_dependency_injection(some_function)


def test_simple_component_without_di():
    """Test that simple components work without DI."""
    result = html(t"<{SimpleComponent} label='Test' />")
    assert str(result) == "<div>Test</div>"


def test_component_with_di_in_context(registry_with_db: HopscotchRegistry):
    """Test that components with DI work when passing context."""
    with HopscotchContainer(registry_with_db) as container:
        result = html(t"<{ButtonWithDI} label='Click Me' />", container=container)

    assert str(result) == "<button>Hello Alice: Click Me</button>"


def test_component_with_multiple_di_dependencies():
    """Test component with multiple DI dependencies."""

    registry = HopscotchRegistry()
    db = DatabaseService()
    auth = AuthService()
    registry.register_value(DatabaseService, db)
    registry.register_value(AuthService, auth)

    with HopscotchContainer(registry) as container:
        result = html(
            t"<{ComplexComponent} title='Admin Panel' />", container=container
        )

    expected = "<div>Admin Panel: User=Alice, Auth=Yes</div>"
    assert str(result) == expected


def test_multiple_components_in_template(registry_with_db: HopscotchRegistry):
    """Test multiple components with and without DI in same template."""
    with HopscotchContainer(registry_with_db) as container:
        result = html(
            t"""
            <div>
                <{SimpleComponent} label='Header' />
                <{ButtonWithDI} label='Login' />
            </div>
        """,
            container=container,
        )

    html_str = str(result)
    assert "<div>Header</div>" in html_str
    assert "<button>Hello Alice: Login</button>" in html_str


def test_nested_components_with_di():
    """Test nested components where child has DI.

    Note: For nested components that render other DI components,
    the container needs to be passed through as a parameter.
    """

    @dataclass
    class ContainerComponent:
        container: HopscotchContainer | None = None

        def __call__(self) -> Template:
            button_html = html(
                t"<{ButtonWithDI} label='Nested' />", container=self.container
            )
            return t"<div class='container'>{button_html}</div>"

    registry_with_db = HopscotchRegistry()
    registry_with_db.register_value(DatabaseService, DatabaseService())

    with HopscotchContainer(registry_with_db) as container:
        result = html(
            t"<{ContainerComponent} container={container} />", container=container
        )

    html_str = str(result)
    assert 'class="container"' in html_str
    assert "Hello Alice: Nested" in html_str


def test_di_context_is_thread_safe():
    """Test that DI works correctly in multi-threaded environments."""

    registry1 = HopscotchRegistry()
    db1 = DatabaseService()
    registry1.register_value(DatabaseService, db1)

    registry2 = HopscotchRegistry()

    class DifferentDB(DatabaseService):
        def get_user(self) -> str:
            return "Bob"

    db2 = DifferentDB()
    registry2.register_value(DatabaseService, db2)

    results = {}

    def thread1_work():
        with HopscotchContainer(registry1) as container:
            result = html(t"<{ButtonWithDI} label='Thread1' />", container=container)
            results["thread1"] = str(result)

    def thread2_work():
        with HopscotchContainer(registry2) as container:
            result = html(t"<{ButtonWithDI} label='Thread2' />", container=container)
            results["thread2"] = str(result)

    t1 = threading.Thread(target=thread1_work)
    t2 = threading.Thread(target=thread2_work)

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    assert "Alice" in results["thread1"]
    assert "Bob" in results["thread2"]


def test_component_with_inject_fails_without_context():
    """DI component raises TypeError when no container is provided."""
    with pytest.raises(TypeError, match="db"):
        html(t"<{ButtonWithDI} label='Test' />")


def test_di_overrides_default_field_value(registry_with_db: HopscotchRegistry):
    """DI injection resolves Inject[T] fields even when a default exists."""

    @dataclass
    class ComponentWithDefault:
        db: Inject[DatabaseService]
        label: str = "Test"

        def __call__(self) -> Template:
            user = self.db.get_user()
            return t"<div>User: {user}, Label: {self.label}</div>"

    with HopscotchContainer(registry_with_db) as container:
        result = html(
            t"<{ComponentWithDefault} label='WithContext' />", container=container
        )

    assert "User: Alice" in str(result)


def test_component_with_children_and_di():
    """Test that components with DI can still receive children parameter."""

    @dataclass
    class Card:
        db: Inject[DatabaseService]
        title: str = "Card"
        children: Template | None = None

        def __call__(self) -> Template:
            user = self.db.get_user()
            return t"<div class='card'><h2>{self.title}</h2><p>User: {user}</p>{self.children}</div>"

    registry_with_db = HopscotchRegistry()
    registry_with_db.register_value(DatabaseService, DatabaseService())

    with HopscotchContainer(registry_with_db) as container:
        result = html(
            t"<{Card} title='Profile'><p>Child content</p></{Card}>",
            container=container,
        )

    html_str = str(result)
    assert "User: Alice" in html_str
    assert "Profile" in html_str
    assert "Child content" in html_str


# Function component DI


def test_function_component_with_inject():
    """Function component with Inject[] gets dependencies injected."""

    def Greeting(db: Inject[DatabaseService], name: str = "World") -> Template:
        user = db.get_user()
        return t"<p>Hello {name}, user is {user}</p>"

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

    def Component(db: Inject[DatabaseService], cache: Inject[CacheService]) -> Template:
        return t"<p>DB: {db.get_user()}, Cache: {cache.get_cached()}</p>"

    registry = HopscotchRegistry()
    registry.register_value(DatabaseService, DatabaseService())
    registry.register_value(CacheService, CacheService())

    with HopscotchContainer(registry) as container:
        result = html(t"<{Component} />", container=container)

    assert "Alice" in str(result)
    assert "cached_value" in str(result)


def test_function_component_inject_without_container_fails():
    """Function component with Inject[] fails without DI container."""

    def Greeting(db: Inject[DatabaseService]) -> Template:
        return t"<p>{db.get_user()}</p>"

    with pytest.raises(TypeError, match="db"):
        html(t"<{Greeting} />")


def test_component_receives_config_via_inject():
    """Config comes from the container via Inject[]."""

    class AppConfig:
        debug = True

    received_config = None

    @dataclass
    class Greeting:
        config: Inject[AppConfig]
        name: str = "World"

        def __call__(self) -> Template:
            nonlocal received_config
            received_config = self.config
            return t"<p>Hello {self.name}</p>"

    registry = HopscotchRegistry()
    cfg = AppConfig()
    registry.register_value(AppConfig, cfg)

    with HopscotchContainer(registry) as container:
        result = html(t"<{Greeting} name='Test' />", container=container)

    assert str(result) == "<p>Hello Test</p>"
    assert received_config is cfg
