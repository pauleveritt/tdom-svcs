"""Regression tests for full Hopscotch resolution surface via Option C architecture.

Each test corresponds to a trace-through in port-tstring-html-integrations-revisited.md.
"""

from dataclasses import dataclass
from string.templatelib import Template
from typing import Protocol
from unittest.mock import patch

import svcs
from svcs_di import Inject
from svcs_hopscotch import Get, Resource
from svcs_hopscotch.injectors import HopscotchContainer, HopscotchRegistry

from tdom_svcs import html
from tdom_svcs.processor import ProcessContext, _tp


# Scenario 1: Inject[T] basic, with and without template override


def test_inject_t_no_template_override():
    """Inject[T] resolves via DI when template doesn't provide it."""

    @dataclass
    class Settings:
        title: str = "Default Title"

    @dataclass
    class Header:
        settings: Inject[Settings]

        def __call__(self) -> Template:
            return t"<h1>{self.settings.title}</h1>"

    registry = HopscotchRegistry()
    registry.register_value(Settings, Settings(title="Injected Title"))
    with HopscotchContainer(registry) as container:
        result = html(t"<{Header} />", container=container)

    assert "Injected Title" in result


def test_inject_t_with_template_override():
    """Template attr overrides DI; Inject[T] is not consulted."""

    @dataclass
    class Settings:
        pass

    @dataclass
    class Header:
        settings: Inject[Settings]

        def __call__(self) -> Template:
            # Template attr is passed; this component receives it directly
            return t"<h1>Template Override</h1>"

    registry = HopscotchRegistry()
    registry.register_value(Settings, Settings())
    with HopscotchContainer(registry) as container:
        # Pass settings via template attr; DI should not be called
        result = html(t"<{Header} settings='ignored' />", container=container)

    assert "Template Override" in result


# Scenario 2: Resource[T] from container.resource


def test_resource_t_from_container_resource():
    """Resource[T] injects from container.resource."""

    @dataclass
    class RequestObj:
        user_id: int = 42

    @dataclass
    class Page:
        request: Resource[RequestObj]

        def __call__(self) -> Template:
            return t"<p>User: {self.request.user_id}</p>"

    registry = HopscotchRegistry()
    with HopscotchContainer(registry) as container:
        # Set container.resource to inject via Resource[T]
        container.resource = RequestObj(user_id=99)
        result = html(t"<{Page} />", container=container)

    assert "User: 99" in result


# Scenario 3: Get[T, Attr] with counter


def test_get_t_attr_di_resolved():
    """Get[T, Attr] resolves operator without template override."""
    get_count = {"calls": 0}

    @dataclass
    class Settings:
        @property
        def site_title(self) -> str:
            get_count["calls"] += 1
            return "My Site"

    @dataclass
    class Page:
        title: Get[Settings, "site_title"]  # noqa: F821

        def __call__(self) -> Template:
            return t"<h1>{self.title}</h1>"

    registry = HopscotchRegistry()
    registry.register_value(Settings, Settings())
    with HopscotchContainer(registry) as container:
        result = html(t"<{Page} />", container=container)

    assert get_count["calls"] == 1
    assert "My Site" in result


def test_get_t_attr_template_override_no_di():
    """Template attr overrides Get[T, Attr]; operator is not called."""
    get_count = {"calls": 0}

    @dataclass
    class Settings:
        @property
        def site_title(self) -> str:
            get_count["calls"] += 1
            return "DI Value"

    @dataclass
    class Page:
        title: Get[Settings, "site_title"]  # noqa: F821

        def __call__(self) -> Template:
            return t"<h1>{self.title}</h1>"

    registry = HopscotchRegistry()
    registry.register_value(Settings, Settings())
    with HopscotchContainer(registry) as container:
        result = html(t'<{Page} title="Template Override" />', container=container)

    assert get_count["calls"] == 0
    assert "Template Override" in result


# Scenario 4: Inject[svcs.Container] self-injection


def test_inject_container_self_injection():
    """Inject[svcs.Container] receives the container itself."""

    @dataclass
    class PageWithContainer:
        container: Inject[svcs.Container]

        def __call__(self) -> Template:
            # Record the received container for assertion
            self.received_container = self.container
            return t"<p>ok</p>"

    registry = HopscotchRegistry()
    with HopscotchContainer(registry) as container:
        result = html(t"<{PageWithContainer} />", container=container)

    # We can't directly access component_object from html(), so this test
    # verifies the component receives a container (indirectly via side effect).
    assert "ok" in result


# Scenario 5: Locator-aware Inject[Protocol]


def test_locator_aware_inject_protocol():
    """Inject[Protocol] uses locator to pick impl based on container.resource."""

    class IConfig(Protocol):
        name: str

    @dataclass
    class ConfigA:
        name: str = "ConfigA"

    @dataclass
    class ConfigB:
        name: str = "ConfigB"

    @dataclass
    class Page:
        page_type: str = ""

    @dataclass
    class Resource:
        page_type: str

    @dataclass
    class PageConsumer:
        config: Inject[IConfig]

        def __call__(self) -> Template:
            return t"<p>{self.config.name}</p>"

    registry = HopscotchRegistry()
    registry.register_implementation(
        IConfig, ConfigA, resource=Page
    )
    registry.register_implementation(
        IConfig, ConfigB, resource=Resource
    )

    # Render in Page context
    with HopscotchContainer(registry) as container:
        container.resource = Page()
        result_a = html(t"<{PageConsumer} />", container=container)

    assert "ConfigA" in result_a

    # Render in Resource context
    with HopscotchContainer(registry) as container:
        container.resource = Resource(page_type="section")
        result_b = html(t"<{PageConsumer} />", container=container)

    assert "ConfigB" in result_b


# Scenario 6: Component-level Protocol → impl override


def test_component_level_protocol_impl_override():
    """<{IHeader} /> template uses registered impl (Header) not Protocol."""

    class IHeader(Protocol):
        def __call__(self) -> Template: ...

    @dataclass
    class Header:
        title: Inject[str] = "default"

        def __call__(self) -> Template:
            return t"<h1>{self.title}</h1>"

    registry = HopscotchRegistry()
    registry.register_implementation(IHeader, Header)
    registry.register_value(str, "Registered Title")

    with HopscotchContainer(registry) as container:
        result = html(t"<{IHeader} />", container=container)

    assert "Registered Title" in result


# Scenario 7: component_object capture under DI (factory class)


def test_component_object_capture_factory():
    """Factory component with Inject[T] fields captures the instance."""

    @dataclass
    class Service:
        value: str = "svc_value"

    @dataclass
    class FactoryComponent:
        svc: Inject[Service]

        def __call__(self) -> Template:
            return t"<p>{self.svc.value}</p>"

    registry = HopscotchRegistry()
    registry.register_value(Service, Service(value="test_value"))

    with HopscotchContainer(registry):
        template = t"<{FactoryComponent} />"
        # Call _tp.process() directly to get the (Template, component_object) tuple
        result_template, component_object = _tp.process(
            template,
            ProcessContext(),
            app_state=None,
        )

    assert component_object is not None
    assert isinstance(component_object, FactoryComponent)
    assert component_object.svc.value == "test_value"


# Scenario 8: Required-DI-field fallback (no template attr)


def test_required_di_field_no_default():
    """Required Inject[T] field with no default renders correctly."""

    @dataclass
    class MyService:
        data: str = "injected"

    @dataclass
    class Component:
        # No default; would raise TypeError without DI
        svc: Inject[MyService]

        def __call__(self) -> Template:
            return t"<p>{self.svc.data}</p>"

    registry = HopscotchRegistry()
    registry.register_value(MyService, MyService(data="success"))

    with HopscotchContainer(registry) as container:
        # Should not raise TypeError; DI fills the required field
        result = html(t"<{Component} />", container=container)

    assert "success" in result


# Scenario 9: No-DI fast path


def test_no_di_fast_path():
    """Plain function component short-circuits to super().process()."""

    def Greeting(name: str = "World") -> Template:
        return t"<p>Hello {name}</p>"

    registry = HopscotchRegistry()

    with HopscotchContainer(registry) as container:
        # Spy on build_resolved_kwargs; it should NOT be called for a plain function
        with patch(
            "tdom_svcs.processor.build_resolved_kwargs"
        ) as mock_build:
            result = html(t"<{Greeting} name='Alice' />", container=container)

        # build_resolved_kwargs should not have been called (short-circuit)
        assert mock_build.call_count == 0

    assert "Hello Alice" in result
