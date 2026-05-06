"""Consumer-shaped component evidence for Tainie judge-confidence tests."""

import json
from dataclasses import asdict, dataclass
from string.templatelib import Template

from svcs_di import Inject
from svcs_hopscotch.injectors import HopscotchContainer, HopscotchRegistry

from tdom_svcs.processor import (
    component_evidence_packet_to_mapping,
    inspect_component_evidence_packet,
)


@dataclass
class _Settings:
    label: str = "injected"


@dataclass
class _Card:
    settings: Inject[_Settings]

    def __call__(self) -> Template:
        return t"<article>{self.settings.label}</article>"


@dataclass
class _CardOverride:
    settings: Inject[_Settings]
    title: str = "Default"

    def __call__(self) -> Template:
        return t"<section>{self.title}: {self.settings.label}</section>"


def test_component_evidence_packet_records_selected_override() -> None:
    registry = HopscotchRegistry()
    registry.register_value(_Settings, _Settings())
    registry.register_implementation(_Card, _CardOverride)

    with HopscotchContainer(registry) as container:
        packet = inspect_component_evidence_packet(
            container,
            _Card,
            {"title": "Template"},
        )

    assert packet.schema_version == "tdom-svcs.component-evidence.v1"
    assert packet.source == "tdom-svcs.processor"
    assert packet.status == "selected"
    assert packet.requested_component == f"{__name__}._Card"
    assert packet.selected_component == f"{__name__}._CardOverride"
    assert packet.implementation_swapped is True
    assert packet.blocker is None
    assert [(field.name, field.source) for field in packet.field_evidence] == [
        ("settings", "injected-dependency"),
        ("title", "template-attr"),
    ]
    assert json.loads(json.dumps(asdict(packet))) == {
        "schema_version": "tdom-svcs.component-evidence.v1",
        "source": "tdom-svcs.processor",
        "status": "selected",
        "requested_component": f"{__name__}._Card",
        "selected_component": f"{__name__}._CardOverride",
        "implementation_swapped": True,
        "field_evidence": [
            {"name": "settings", "source": "injected-dependency"},
            {"name": "title", "source": "template-attr"},
        ],
        "blocker": None,
    }


def test_component_evidence_packet_maps_selected_override_to_report_shape() -> None:
    registry = HopscotchRegistry()
    registry.register_value(_Settings, _Settings())
    registry.register_implementation(_Card, _CardOverride)

    with HopscotchContainer(registry) as container:
        packet = inspect_component_evidence_packet(
            container,
            _Card,
            {"title": "Template"},
        )

    assert component_evidence_packet_to_mapping(packet) == {
        "schema_version": "component-evidence.v1",
        "source": "tdom-svcs.processor",
        "status": "observed",
        "component": f"{__name__}._Card",
        "evidence": [
            f"requested={__name__}._Card",
            f"selected={__name__}._CardOverride",
            "implementation_swapped=true",
            "field:settings:injected-dependency",
            "field:title:template-attr",
        ],
    }


def test_component_evidence_packet_maps_required_di_blocker_to_report_shape() -> None:
    packet = inspect_component_evidence_packet(None, _Card, {})

    assert component_evidence_packet_to_mapping(packet) == {
        "schema_version": "component-evidence.v1",
        "source": "tdom-svcs.processor",
        "status": "blocked",
        "component": f"{__name__}._Card",
        "evidence": [
            f"requested={__name__}._Card",
            "selected=None",
            "implementation_swapped=false",
            "blocker=container_required",
        ],
    }


def test_component_evidence_packet_records_no_container_plain_component() -> None:
    def Greeting(name: str = "World") -> Template:
        return t"<p>Hello {name}</p>"

    packet = inspect_component_evidence_packet(None, Greeting, {"name": "Alice"})

    assert packet.status == "no-container"
    assert packet.selected_component == f"{__name__}.{Greeting.__qualname__}"
    assert packet.implementation_swapped is False
    assert packet.field_evidence == ()
    assert packet.blocker is None


def test_component_evidence_packet_records_required_di_without_container() -> None:
    packet = inspect_component_evidence_packet(None, _Card, {})

    assert packet.status == "requires-di-container"
    assert packet.selected_component is None
    assert packet.implementation_swapped is False
    assert packet.field_evidence == ()
    assert packet.blocker == "container_required"


def test_component_evidence_packet_uses_qualname_for_nested_components() -> None:
    class Wrapper:
        class Nested:
            def __call__(self) -> Template:
                return t"<p>Nested</p>"

    packet = inspect_component_evidence_packet(None, Wrapper.Nested, {})

    assert packet.requested_component == f"{__name__}.{Wrapper.Nested.__qualname__}"
    assert packet.selected_component == f"{__name__}.{Wrapper.Nested.__qualname__}"
