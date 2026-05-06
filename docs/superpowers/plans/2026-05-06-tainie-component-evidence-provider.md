# Tainie Component Evidence Provider Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `tdom-svcs` component evidence available to Tainie through an opt-in component provider lane with native and Pydantic Evals parity.

**Architecture:** `tdom-svcs` keeps owning the detailed component inspection packet and adds a small helper that projects it into Tainie's trusted component report shape. Tainie adds `component_provider` fixture metadata, a component producer registry parallel to the existing route producer registry, strict projection validation, and tests showing native plus Pydantic evals consume the provider without importing `tdom_svcs` by default.

**Tech Stack:** Python 3.14, Pydantic v2, pytest, uv, Ruff, ty, `tdom-svcs`, Tainie eval provider registry.

**Commit Policy:** The local `tdom-svcs` `AGENTS.md` says not to automatically commit while implementing a plan. Treat each task-end checkpoint as a review boundary; only run `git commit` if the user explicitly asks.

---

## File Structure

### tdom-svcs

- Modify `src/tdom_svcs/processor.py`
  - Add `component_evidence_packet_to_mapping(packet)`.
  - Keep `inspect_component_evidence_packet()` and rendering behavior unchanged.
- Modify `tests/test_judge_confidence_evidence.py`
  - Add tests for the new mapping helper.
  - Keep current packet behavior tests intact.

### Tainie

- Modify `/Users/pauleveritt/projects/t-strings/tainie/src/tainie/eval/fixtures.py`
  - Add `component_provider: str | None` to fixture metadata and resolved fixtures.
- Modify `/Users/pauleveritt/projects/t-strings/tainie/src/tainie/eval/evidence_providers.py`
  - Add component producer types, registry, registration helper, provider factory, and projection adapter.
  - Add the component provider factory to `DEFAULT_EVIDENCE_PROVIDER_REGISTRY`.
- Modify `/Users/pauleveritt/projects/t-strings/tainie/tests/test_eval_fixtures.py`
  - Prove fixture TOML preserves `component_provider`.
- Modify `/Users/pauleveritt/projects/t-strings/tainie/tests/test_evidence_providers.py`
  - Prove component provider dispatch, mapping/projection support, missing producer behavior, malformed projection failure, and registration import discipline.
- Modify `/Users/pauleveritt/projects/t-strings/tainie/tests/test_eval_runner.py`
  - Prove public native eval entrypoints consume component provider evidence and quarantine malformed component provider output.
- Modify `/Users/pauleveritt/projects/t-strings/tainie/tests/test_pydantic_evals_adapter.py`
  - Prove Pydantic Evals grouped runs get the same component evidence counts.

---

### Task 1: Add tdom-svcs Component Report Projection

**Files:**
- Modify: `src/tdom_svcs/processor.py`
- Modify: `tests/test_judge_confidence_evidence.py`

- [ ] **Step 1: Write failing tests for report-shape projection**

In `tests/test_judge_confidence_evidence.py`, update the import:

```python
from tdom_svcs.processor import (
    component_evidence_packet_to_mapping,
    inspect_component_evidence_packet,
)
```

Add these tests after `test_component_evidence_packet_records_selected_override`:

```python
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
```

- [ ] **Step 2: Run the focused failing tests**

Run:

```bash
uv run pytest tests/test_judge_confidence_evidence.py -q
```

Expected: FAIL because `component_evidence_packet_to_mapping` is not defined or not imported.

- [ ] **Step 3: Implement the mapping helper**

In `src/tdom_svcs/processor.py`, add the function near `inspect_component_evidence_packet()`:

```python
def component_evidence_packet_to_mapping(
    packet: ComponentEvidencePacket,
) -> dict[str, object]:
    """Project a detailed tdom-svcs packet into a trusted component report shape."""
    status = "blocked" if packet.status == "requires-di-container" else "observed"
    selected = packet.selected_component if packet.selected_component is not None else "None"
    evidence = [
        f"requested={packet.requested_component}",
        f"selected={selected}",
        f"implementation_swapped={str(packet.implementation_swapped).lower()}",
    ]
    evidence.extend(
        f"field:{field.name}:{field.source}" for field in packet.field_evidence
    )
    if packet.blocker is not None:
        evidence.append(f"blocker={packet.blocker}")

    return {
        "schema_version": "component-evidence.v1",
        "source": packet.source,
        "status": status,
        "component": packet.requested_component,
        "evidence": evidence,
    }
```

Do not add this helper to `tdom_svcs.__init__`; keep `from tdom_svcs import html` as the obvious first move and leave evidence helpers under `tdom_svcs.processor`.

- [ ] **Step 4: Verify tdom-svcs focused tests pass**

Run:

```bash
uv run pytest tests/test_judge_confidence_evidence.py -q
```

Expected: PASS.

- [ ] **Step 5: Verify tdom-svcs quality for touched surface**

Run:

```bash
uv run ruff check src/tdom_svcs/processor.py tests/test_judge_confidence_evidence.py
uv run ruff format --check src/tdom_svcs/processor.py tests/test_judge_confidence_evidence.py
uv run ty check src/tdom_svcs/processor.py tests/test_judge_confidence_evidence.py
```

Expected: all commands pass.

- [ ] **Step 6: Review checkpoint**

Run:

```bash
git diff -- src/tdom_svcs/processor.py tests/test_judge_confidence_evidence.py
```

Expected: diff only adds the projection helper and mapping tests; no rendering behavior changes.

---

### Task 2: Add Tainie component_provider Fixture Metadata

**Files:**
- Modify: `/Users/pauleveritt/projects/t-strings/tainie/src/tainie/eval/fixtures.py`
- Modify: `/Users/pauleveritt/projects/t-strings/tainie/tests/test_eval_fixtures.py`

- [ ] **Step 1: Write failing fixture metadata test**

In `/Users/pauleveritt/projects/t-strings/tainie/tests/test_eval_fixtures.py`, add this test near `test_load_fixture_preserves_route_provider_name`:

```python
def test_load_fixture_preserves_component_provider_name(tmp_path: Path) -> None:
    fixture_dir = _write_fixture(tmp_path)
    fixture_toml = fixture_dir / "fixture.toml"
    fixture_toml.write_text(
        f'{fixture_toml.read_text(encoding="utf-8")}\n'
        'component_provider = "tdom-svcs"\n',
        encoding="utf-8",
    )

    fixture = load_fixture(fixture_dir)

    assert fixture.component_provider == "tdom-svcs"
```

- [ ] **Step 2: Run the focused failing test**

Run from `/Users/pauleveritt/projects/t-strings/tainie`:

```bash
uv run pytest tests/test_eval_fixtures.py::test_load_fixture_preserves_component_provider_name -q
```

Expected: FAIL because extra `component_provider` metadata is forbidden or `EvalFixture` has no such attribute.

- [ ] **Step 3: Add component_provider to fixture models**

In `/Users/pauleveritt/projects/t-strings/tainie/src/tainie/eval/fixtures.py`, add `component_provider` beside `route_provider`:

```python
class FixtureMetadata(BaseModel):
    """Raw fixture.toml contract."""

    model_config = ConfigDict(extra="forbid")

    id: FixtureId
    suite: EvalSuite
    task: str
    input_dir: str
    public_verifier: VerifierCommandText
    hidden_verifier: VerifierCommandText
    rubrics: list[RubricName]
    expected: ExpectedOutcome
    max_tool_calls: MaxToolCalls | None = None
    route_artifact: str | None = None
    route_provider: str | None = None
    component_provider: str | None = None
```

```python
class EvalFixture(BaseModel):
    """Resolved fixture ready for execution."""

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    fixture_id: FixtureId
    suite: EvalSuite
    task: str
    root: Path
    input_dir: Path
    public_verifier: VerifierCommand
    hidden_verifier: VerifierCommand
    rubrics: list[RubricName]
    expected: ExpectedOutcome
    max_tool_calls: MaxToolCalls | None = None
    route_artifact: Path | None = None
    route_provider: str | None = None
    component_provider: str | None = None
```

In `load_fixture()`, pass the field into `EvalFixture`:

```python
        route_artifact=route_artifact_path,
        route_provider=metadata.route_provider,
        component_provider=metadata.component_provider,
```

- [ ] **Step 4: Verify fixture test passes**

Run:

```bash
uv run pytest tests/test_eval_fixtures.py::test_load_fixture_preserves_component_provider_name -q
```

Expected: PASS.

- [ ] **Step 5: Verify existing fixture tests still pass**

Run:

```bash
uv run pytest tests/test_eval_fixtures.py -q
```

Expected: PASS.

---

### Task 3: Add Tainie Component Evidence Provider Registry

**Files:**
- Modify: `/Users/pauleveritt/projects/t-strings/tainie/src/tainie/eval/evidence_providers.py`
- Modify: `/Users/pauleveritt/projects/t-strings/tainie/tests/test_evidence_providers.py`

- [ ] **Step 1: Write failing provider tests**

In `/Users/pauleveritt/projects/t-strings/tainie/tests/test_evidence_providers.py`, update imports:

```python
from tainie.eval.evidence_providers import (
    COMPONENT_EVIDENCE_PRODUCERS,
    DEFAULT_EVIDENCE_PROVIDER_REGISTRY,
    HOPSCOTCH_ROUTE_PRODUCERS,
    component_evidence_provider_for,
    component_projection_to_report,
    compose_evidence_providers,
    default_evidence_provider,
    hopscotch_locator_explanation_to_route_artifact,
    hopscotch_route_provider_for,
    register_svcs_hopscotch_route_producer,
    register_tdom_svcs_component_producer,
    route_artifact_provider_for,
)
```

Update `_fixture()` so tests can opt into component evidence:

```python
def _fixture(
    tmp_path: Path,
    *,
    route_artifact: Path | None = None,
    route_provider: str | None = None,
    component_provider: str | None = None,
) -> EvalFixture:
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "app.py").write_text("", encoding="utf-8")
    return EvalFixture(
        fixture_id="route_fixture_001",
        suite="smoke",
        task="No code change is required.",
        root=tmp_path,
        input_dir=input_dir,
        public_verifier=VerifierCommand(command='{python} -c "raise SystemExit(0)"'),
        hidden_verifier=VerifierCommand(command='{python} -c "raise SystemExit(0)"'),
        rubrics=[],
        expected="ACCEPT",
        route_artifact=route_artifact,
        route_provider=route_provider,
        component_provider=component_provider,
    )
```

Add this projection helper class near `FakeLocatorExplanation`:

```python
class FakeComponentProjection:
    def __init__(self, payload: Mapping[str, object]) -> None:
        self.payload = payload

    def as_component_evidence_v1(self) -> Mapping[str, object]:
        return self.payload
```

Add this payload helper near `_route_payload()`:

```python
def _component_report_payload(
    *,
    status: str = "observed",
    component: str = "tests.Card",
) -> dict[str, object]:
    return {
        "schema_version": "component-evidence.v1",
        "source": "tdom-svcs.processor",
        "status": status,
        "component": component,
        "evidence": [
            f"requested={component}",
            f"selected={component}",
            "implementation_swapped=false",
        ],
    }
```

Add these tests after the existing route provider tests:

```python
def test_component_projection_to_report_validates_report_mapping() -> None:
    report = component_projection_to_report(_component_report_payload())

    assert report.schema_version == "component-evidence.v1"
    assert report.source == "tdom-svcs.processor"
    assert report.status == "observed"
    assert report.component == "tests.Card"


def test_component_projection_to_report_accepts_projection_object() -> None:
    report = component_projection_to_report(
        FakeComponentProjection(_component_report_payload(component="tests.Panel"))
    )

    assert report.component == "tests.Panel"
    assert report.status == "observed"


def test_component_projection_to_report_maps_tdom_svcs_packet_shape() -> None:
    report = component_projection_to_report(
        {
            "schema_version": "tdom-svcs.component-evidence.v1",
            "source": "tdom-svcs.processor",
            "status": "requires-di-container",
            "requested_component": "tests.Card",
            "selected_component": None,
            "implementation_swapped": False,
            "field_evidence": [],
            "blocker": "container_required",
        }
    )

    assert report.schema_version == "component-evidence.v1"
    assert report.status == "blocked"
    assert report.component == "tests.Card"
    assert report.evidence == [
        "requested=tests.Card",
        "selected=None",
        "implementation_swapped=false",
        "blocker=container_required",
    ]


def test_component_evidence_provider_returns_report(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _fixture(tmp_path, component_provider="contract-smoke")
    monkeypatch.setitem(
        COMPONENT_EVIDENCE_PRODUCERS,
        "contract-smoke",
        lambda fixture, workspace: _component_report_payload(component=fixture.fixture_id),
    )

    provider = component_evidence_provider_for(fixture)

    assert provider is not None
    packets = provider(fixture, tmp_path / "workspace")
    assert len(packets) == 1
    assert packets[0].schema_version == "component-evidence.v1"
    assert packets[0].source == "tdom-svcs.processor"
    assert packets[0].status == "observed"
    assert packets[0].component == fixture.fixture_id


def test_default_evidence_provider_combines_route_and_component_providers(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact = tmp_path / "route_inspection" / "selected_layout.json"
    _write_route_artifact(artifact)
    fixture = _fixture(
        tmp_path,
        route_artifact=artifact,
        component_provider="contract-smoke",
    )
    monkeypatch.setitem(
        COMPONENT_EVIDENCE_PRODUCERS,
        "contract-smoke",
        lambda fixture, workspace: _component_report_payload(),
    )

    packets = default_evidence_provider(fixture, tmp_path / "workspace")

    assert [packet.schema_version for packet in packets] == [
        "route-inspection.v1",
        "component-evidence.v1",
    ]


def test_component_evidence_provider_allows_missing_producer(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path, component_provider="not-registered")

    assert component_evidence_provider_for(fixture) is None
    assert default_evidence_provider(fixture, tmp_path / "workspace") == []


def test_component_evidence_provider_allows_none_projection(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _fixture(tmp_path, component_provider="contract-smoke")
    monkeypatch.setitem(
        COMPONENT_EVIDENCE_PRODUCERS,
        "contract-smoke",
        lambda fixture, workspace: None,
    )

    provider = component_evidence_provider_for(fixture)

    assert provider is not None
    assert provider(fixture, tmp_path / "workspace") == []


def test_component_evidence_provider_raises_for_malformed_projection(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _fixture(tmp_path, component_provider="contract-smoke")
    monkeypatch.setitem(
        COMPONENT_EVIDENCE_PRODUCERS,
        "contract-smoke",
        lambda fixture, workspace: {"schema_version": "wrong"},
    )

    provider = component_evidence_provider_for(fixture)

    assert provider is not None
    with pytest.raises(ValidationError):
        provider(fixture, tmp_path / "workspace")


def test_register_tdom_svcs_component_producer_registers_when_package_available(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _fixture(tmp_path, component_provider="tdom-svcs")
    monkeypatch.delitem(COMPONENT_EVIDENCE_PRODUCERS, "tdom-svcs", raising=False)

    registered = register_tdom_svcs_component_producer(
        lambda fixture, workspace: _component_report_payload(component=fixture.fixture_id)
    )

    assert registered is True
    packets = default_evidence_provider(fixture, tmp_path / "workspace")
    assert len(packets) == 1
    assert packets[0].schema_version == "component-evidence.v1"
    assert packets[0].component == fixture.fixture_id


def test_register_tdom_svcs_component_producer_allows_package_absence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def missing_import(name: str) -> object:
        raise ModuleNotFoundError(name, name="tdom_svcs")

    fixture = _fixture(tmp_path, component_provider="tdom-svcs")
    monkeypatch.delitem(COMPONENT_EVIDENCE_PRODUCERS, "tdom-svcs", raising=False)

    registered = register_tdom_svcs_component_producer(
        lambda fixture, workspace: None,
        import_module=missing_import,
    )

    assert registered is False
    assert "tdom-svcs" not in COMPONENT_EVIDENCE_PRODUCERS
    assert default_evidence_provider(fixture, tmp_path / "workspace") == []


def test_register_tdom_svcs_component_producer_reraises_internal_import_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def broken_import(name: str) -> object:
        raise ModuleNotFoundError(name, name="tdom_svcs.dependency")

    monkeypatch.delitem(COMPONENT_EVIDENCE_PRODUCERS, "tdom-svcs", raising=False)

    with pytest.raises(ModuleNotFoundError) as error:
        register_tdom_svcs_component_producer(
            lambda fixture, workspace: None,
            import_module=broken_import,
        )

    assert error.value.name == "tdom_svcs.dependency"
    assert "tdom-svcs" not in COMPONENT_EVIDENCE_PRODUCERS
```

- [ ] **Step 2: Run the focused failing provider tests**

Run from `/Users/pauleveritt/projects/t-strings/tainie`:

```bash
uv run pytest tests/test_evidence_providers.py -q
```

Expected: FAIL because component provider symbols do not exist.

- [ ] **Step 3: Implement component provider support**

In `/Users/pauleveritt/projects/t-strings/tainie/src/tainie/eval/evidence_providers.py`, update imports:

```python
from collections.abc import Callable, Iterable, Mapping
from dataclasses import asdict, dataclass, is_dataclass
from importlib import import_module as import_module_object
from pathlib import Path
from typing import Protocol, TypeGuard

from tainie.domain.decision_evidence import (
    ComponentEvidenceReport,
    RouteInspectionArtifact,
    TrustedEvidencePacket,
    load_route_inspection_artifact,
    report_route_inspection,
)
```

Add component projection and producer types after the route producer types:

```python
class ComponentEvidenceProjection(Protocol):
    def as_component_evidence_v1(self) -> Mapping[str, object]: ...


type ComponentEvidenceProducer = Callable[
    [EvalFixture, Path],
    object | None,
]

COMPONENT_EVIDENCE_PRODUCERS: dict[str, ComponentEvidenceProducer] = {}
```

Add provider factory after `hopscotch_route_provider_for()`:

```python
def component_evidence_provider_for(fixture: EvalFixture) -> EvidenceProvider | None:
    producer_name = fixture.component_provider
    if producer_name is None:
        return None
    producer = COMPONENT_EVIDENCE_PRODUCERS.get(producer_name)
    if producer is None:
        return None

    def provider(
        fixture: EvalFixture,
        workspace: Path,
    ) -> list[TrustedEvidencePacket]:
        projection = producer(fixture, workspace)
        if projection is None:
            return []
        return [component_projection_to_report(projection)]

    return provider
```

Add registration helper after `register_svcs_hopscotch_route_producer()`:

```python
def register_tdom_svcs_component_producer(
    producer: ComponentEvidenceProducer,
    *,
    name: str = "tdom-svcs",
    import_module: Callable[[str], object] = import_module_object,
) -> bool:
    try:
        import_module("tdom_svcs")
    except ModuleNotFoundError as exc:
        if exc.name == "tdom_svcs":
            return False
        raise
    COMPONENT_EVIDENCE_PRODUCERS[name] = producer
    return True
```

Add projection helpers after route conversion helpers:

```python
def component_projection_to_report(projection: object) -> ComponentEvidenceReport:
    if isinstance(projection, Mapping):
        return _component_mapping_to_report(projection)
    if _is_component_evidence_projection(projection):
        return _component_mapping_to_report(projection.as_component_evidence_v1())
    if is_dataclass(projection) and not isinstance(projection, type):
        return _component_mapping_to_report(asdict(projection))
    return _component_mapping_to_report(_component_packet_object_to_mapping(projection))


def _component_mapping_to_report(
    payload: Mapping[str, object],
) -> ComponentEvidenceReport:
    if payload.get("schema_version") == "tdom-svcs.component-evidence.v1":
        return _tdom_svcs_component_packet_to_report(payload)
    return ComponentEvidenceReport.model_validate(payload)


def _tdom_svcs_component_packet_to_report(
    payload: Mapping[str, object],
) -> ComponentEvidenceReport:
    status = payload.get("status")
    if status == "requires-di-container":
        report_status = "blocked"
    elif status in {"selected", "no-container"}:
        report_status = "observed"
    else:
        msg = f"unknown tdom-svcs component evidence status: {status!r}"
        raise TypeError(msg)

    requested_component = _required_text(payload, "requested_component")
    selected_component = payload.get("selected_component")
    if selected_component is not None and not isinstance(selected_component, str):
        msg = "tdom-svcs component evidence selected_component must be a string or None"
        raise TypeError(msg)

    implementation_swapped = payload.get("implementation_swapped")
    if not isinstance(implementation_swapped, bool):
        msg = "tdom-svcs component evidence implementation_swapped must be bool"
        raise TypeError(msg)

    evidence = [
        f"requested={requested_component}",
        f"selected={selected_component if selected_component is not None else 'None'}",
        f"implementation_swapped={str(implementation_swapped).lower()}",
    ]
    field_evidence = payload.get("field_evidence")
    if not isinstance(field_evidence, list | tuple):
        msg = "tdom-svcs component evidence field_evidence must be a sequence"
        raise TypeError(msg)
    for field in field_evidence:
        if not isinstance(field, Mapping):
            msg = "tdom-svcs component evidence field entries must be mappings"
            raise TypeError(msg)
        evidence.append(
            f"field:{_required_text(field, 'name')}:{_required_text(field, 'source')}"
        )

    blocker = payload.get("blocker")
    if blocker is not None:
        if not isinstance(blocker, str):
            msg = "tdom-svcs component evidence blocker must be a string or None"
            raise TypeError(msg)
        evidence.append(f"blocker={blocker}")

    return ComponentEvidenceReport(
        schema_version="component-evidence.v1",
        source=_required_text(payload, "source"),
        status=report_status,
        component=requested_component,
        evidence=evidence,
    )


def _component_packet_object_to_mapping(projection: object) -> Mapping[str, object]:
    return {
        "schema_version": _required_attribute(projection, "schema_version"),
        "source": _required_attribute(projection, "source"),
        "status": _required_attribute(projection, "status"),
        "requested_component": _required_attribute(projection, "requested_component"),
        "selected_component": _required_attribute(projection, "selected_component"),
        "implementation_swapped": _required_attribute(
            projection,
            "implementation_swapped",
        ),
        "field_evidence": _required_attribute(projection, "field_evidence"),
        "blocker": _required_attribute(projection, "blocker"),
    }


def _is_component_evidence_projection(
    value: object,
) -> TypeGuard[ComponentEvidenceProjection]:
    return hasattr(value, "as_component_evidence_v1")


def _required_text(payload: Mapping[str, object], name: str) -> str:
    value = payload.get(name)
    if not isinstance(value, str):
        msg = f"tdom-svcs component evidence {name} must be a string"
        raise TypeError(msg)
    return value
```

Update the default registry:

```python
DEFAULT_EVIDENCE_PROVIDER_REGISTRY = EvidenceProviderRegistry(
    provider_factories=(
        route_artifact_provider_for,
        hopscotch_route_provider_for,
        component_evidence_provider_for,
    ),
)
```

- [ ] **Step 4: Verify provider tests pass**

Run:

```bash
uv run pytest tests/test_evidence_providers.py -q
```

Expected: PASS.

- [ ] **Step 5: Run provider type and lint checks**

Run:

```bash
uv run ruff check src/tainie/eval/evidence_providers.py tests/test_evidence_providers.py
uv run ruff format --check src/tainie/eval/evidence_providers.py tests/test_evidence_providers.py
uv run ty check src/tainie/eval/evidence_providers.py tests/test_evidence_providers.py
```

Expected: all commands pass.

---

### Task 4: Prove Native Eval Entrypoints Consume Component Evidence

**Files:**
- Modify: `/Users/pauleveritt/projects/t-strings/tainie/tests/test_eval_runner.py`

- [ ] **Step 1: Write failing native eval tests**

In `/Users/pauleveritt/projects/t-strings/tainie/tests/test_eval_runner.py`, update evidence provider imports:

```python
from tainie.eval.evidence_providers import (
    COMPONENT_EVIDENCE_PRODUCERS,
    HOPSCOTCH_ROUTE_PRODUCERS,
    register_svcs_hopscotch_route_producer,
)
```

Update the local `_fixture()` helper to accept and pass `component_provider`:

```python
def _fixture(
    tmp_path: Path,
    *,
    fixture_id: str = "component_label_001",
    public: str = 'raise SystemExit("public failed")\n',
    hidden: str = 'raise SystemExit("hidden failed")\n',
    suite: Literal["smoke", "full", "themester", "evidence_canary"] = "smoke",
    expected: Literal["ACCEPT", "REJECT"] = "ACCEPT",
    max_tool_calls: int | None = None,
    route_artifact: Path | None = None,
    route_provider: str | None = None,
    component_provider: str | None = None,
) -> EvalFixture:
    ...
        route_artifact=route_artifact,
        route_provider=route_provider,
        component_provider=component_provider,
    )
```

Add this helper near the route payload helpers:

```python
def _component_evidence_payload(
    *,
    status: str = "observed",
    component: str = "tests.Card",
) -> dict[str, object]:
    return {
        "schema_version": "component-evidence.v1",
        "source": "tdom-svcs.processor",
        "status": status,
        "component": component,
        "evidence": [
            f"requested={component}",
            f"selected={component}",
            "implementation_swapped=false",
            "field:settings:injected-dependency",
        ],
    }
```

Add these tests near the route provider entrypoint tests:

```python
def test_run_eval_fixture_uses_component_provider_contract(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    written: list[RunRecord] = []
    fixture = _fixture(
        tmp_path,
        public="raise SystemExit(0)\n",
        hidden="raise SystemExit(0)\n",
        component_provider="contract-smoke",
    )

    monkeypatch.setattr("tainie.eval.runner.load_fixture", lambda path: fixture)
    monkeypatch.setattr("tainie.eval.runner.ensure_model_staged", lambda: None)
    monkeypatch.setattr(
        "tainie.eval.runner.check_omlx_ready",
        lambda *, base_url: OmlxReadiness(base_url=base_url, model_id="Qwen3-8B"),
    )
    monkeypatch.setattr("tainie.eval.metrics.current_git_sha", lambda: ("abc123", []))
    monkeypatch.setattr("tainie.eval.metrics.write_run_record", written.append)
    monkeypatch.setattr(
        "tainie.eval.runner.run_live_fixture_agent",
        lambda fixture, workspace, *, base_url, lhs: TaskOutcome(
            success=True,
            summary="no-op",
        ),
    )
    monkeypatch.setitem(
        COMPONENT_EVIDENCE_PRODUCERS,
        "contract-smoke",
        lambda fixture, workspace: _component_evidence_payload(
            component=fixture.fixture_id
        ),
    )

    record = run_eval_fixture(
        fixture_id="ignored_by_monkeypatch",
        base_url="http://example.test/v1",
    )

    assert written == [record]
    evidence = record.fixtures[0].trusted_evidence[0]
    assert isinstance(evidence, ComponentEvidenceReport)
    assert evidence.schema_version == "component-evidence.v1"
    assert evidence.source == "tdom-svcs.processor"
    assert evidence.status == "observed"
    assert evidence.component == fixture.fixture_id
    assert "field:settings:injected-dependency" in evidence.evidence
```

```python
def test_run_eval_fixture_quarantines_malformed_component_projection(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    fixture = _fixture(
        tmp_path,
        public="raise SystemExit(0)\n",
        hidden="raise SystemExit(0)\n",
        component_provider="contract-smoke",
    )

    monkeypatch.setattr("tainie.eval.runner.load_fixture", lambda path: fixture)
    monkeypatch.setattr("tainie.eval.runner.ensure_model_staged", lambda: None)
    monkeypatch.setattr(
        "tainie.eval.runner.check_omlx_ready",
        lambda *, base_url: OmlxReadiness(base_url=base_url, model_id="Qwen3-8B"),
    )
    monkeypatch.setattr("tainie.eval.metrics.current_git_sha", lambda: ("abc123", []))
    monkeypatch.setattr("tainie.eval.metrics.write_run_record", lambda record: None)
    monkeypatch.setattr(
        "tainie.eval.runner.run_live_fixture_agent",
        lambda fixture, workspace, *, base_url, lhs: TaskOutcome(
            success=True,
            summary="no-op",
        ),
    )
    monkeypatch.setitem(
        COMPONENT_EVIDENCE_PRODUCERS,
        "contract-smoke",
        lambda fixture, workspace: {"schema_version": "wrong"},
    )

    record = run_eval_fixture(
        fixture_id="ignored_by_monkeypatch",
        base_url="http://example.test/v1",
    )

    result = record.fixtures[0]
    assert result.outcome == "BLOCKED"
    assert result.blocker == "evidence_provider_failure"
    assert result.self_assessment is not None
    assert "component-evidence.v1" in result.self_assessment.summary
```

Add grouped native suite coverage near `test_run_eval_suite_groups_hopscotch_route_provider_contract`:

```python
def test_run_eval_suite_groups_component_provider_contract(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    fixtures = [
        _fixture(
            tmp_path,
            fixture_id="component_selected",
            public="raise SystemExit(0)\n",
            hidden="raise SystemExit(0)\n",
            component_provider="contract-smoke",
        )
    ]
    written_runs: list[RunRecord] = []
    written_groups: list[RunGroupRecord] = []

    monkeypatch.setattr("tainie.eval.runner.ensure_model_staged", lambda: None)
    monkeypatch.setattr(
        "tainie.eval.runner.check_omlx_ready",
        lambda *, base_url: OmlxReadiness(base_url=base_url, model_id="Qwen3-8B"),
    )
    monkeypatch.setattr("tainie.eval.runner.discover_fixtures", lambda *, suite: fixtures)
    monkeypatch.setattr("tainie.eval.metrics.current_git_sha", lambda: ("abc123", []))
    monkeypatch.setattr("tainie.eval.metrics.write_run_record", written_runs.append)
    monkeypatch.setattr(
        "tainie.eval.metrics.write_run_group_record",
        written_groups.append,
    )
    monkeypatch.setattr(
        "tainie.eval.runner.run_live_fixture_agent",
        lambda fixture, workspace, *, base_url, lhs: TaskOutcome(
            success=True,
            summary="no-op",
        ),
    )
    monkeypatch.setitem(
        COMPONENT_EVIDENCE_PRODUCERS,
        "contract-smoke",
        lambda fixture, workspace: _component_evidence_payload(
            component=fixture.fixture_id
        ),
    )

    record = run_eval_suite(
        suite="smoke",
        base_url="http://example.test/v1",
        trials=2,
    )

    assert isinstance(record, RunGroupRecord)
    assert written_groups == [record]
    assert record.trusted_evidence_counts == {
        ("component-evidence.v1", "tdom-svcs.processor", "observed"): 2
    }
```

- [ ] **Step 2: Run focused native eval tests**

Run:

```bash
uv run pytest \
  tests/test_eval_runner.py::test_run_eval_fixture_uses_component_provider_contract \
  tests/test_eval_runner.py::test_run_eval_fixture_quarantines_malformed_component_projection \
  tests/test_eval_runner.py::test_run_eval_suite_groups_component_provider_contract \
  -q
```

Expected: PASS once Tasks 2 and 3 are complete.

- [ ] **Step 3: Run nearby native eval regression tests**

Run:

```bash
uv run pytest tests/test_eval_runner.py -q
```

Expected: PASS.

---

### Task 5: Prove Pydantic Evals Parity

**Files:**
- Modify: `/Users/pauleveritt/projects/t-strings/tainie/tests/test_pydantic_evals_adapter.py`

- [ ] **Step 1: Write failing Pydantic parity test**

In `/Users/pauleveritt/projects/t-strings/tainie/tests/test_pydantic_evals_adapter.py`, update imports:

```python
from tainie.eval.evidence_providers import (
    COMPONENT_EVIDENCE_PRODUCERS,
    HOPSCOTCH_ROUTE_PRODUCERS,
)
```

Update the local `_fixture()` helper to accept and pass `component_provider`:

```python
def _fixture(
    tmp_path: Path,
    *,
    fixture_id: str = "component_label_001",
    suite: EvalSuite = "smoke",
    expected: ExpectedOutcome = "ACCEPT",
    rubrics: list[str] | None = None,
    route_artifact: Path | None = None,
    route_provider: str | None = None,
    component_provider: str | None = None,
) -> EvalFixture:
    ...
        route_artifact=route_artifact,
        route_provider=route_provider,
        component_provider=component_provider,
    )
```

Add this helper near `_route_payload()`:

```python
def _component_evidence_payload(
    *,
    status: str = "observed",
    component: str = "tests.Card",
) -> dict[str, object]:
    return {
        "schema_version": "component-evidence.v1",
        "source": "tdom-svcs.processor",
        "status": status,
        "component": component,
        "evidence": [
            f"requested={component}",
            f"selected={component}",
            "implementation_swapped=false",
        ],
    }
```

Add this test near `test_run_pydantic_eval_suite_writes_grouped_evidence_records`:

```python
def test_run_pydantic_eval_suite_writes_grouped_component_evidence_records(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixtures = [
        _fixture(
            tmp_path,
            fixture_id="component_selected",
            rubrics=[],
            component_provider="contract-smoke",
        )
    ]
    writes: list[RunRecord | RunGroupRecord] = []

    monkeypatch.setattr(
        "tainie.eval.pydantic_evals_adapter.ensure_model_staged",
        lambda: tmp_path / "model",
    )
    monkeypatch.setattr(
        "tainie.eval.pydantic_evals_adapter.check_omlx_ready",
        lambda *, base_url: SimpleNamespace(model_id="Qwen3-8B", base_url=base_url),
    )
    monkeypatch.setattr(
        "tainie.eval.pydantic_evals_adapter.current_git_sha",
        lambda: ("abcdef123456", []),
    )
    monkeypatch.setattr(
        "tainie.eval.pydantic_evals_adapter.discover_fixtures",
        lambda *, suite: fixtures,
    )
    monkeypatch.setattr(
        "tainie.eval.pydantic_evals_adapter.write_run_record",
        lambda record: writes.append(record),
    )
    monkeypatch.setattr(
        "tainie.eval.pydantic_evals_adapter.write_run_group_record",
        lambda record: writes.append(record),
    )
    monkeypatch.setitem(
        COMPONENT_EVIDENCE_PRODUCERS,
        "contract-smoke",
        lambda fixture, workspace: _component_evidence_payload(
            component=fixture.fixture_id
        ),
    )

    result = run_pydantic_eval_suite(
        suite="smoke",
        base_url="http://example.test/v1",
        trials=2,
        agent_runner=_agent_runner,
    )

    assert isinstance(result.record, RunGroupRecord)
    assert writes == [*result.raw_records, result.record]
    assert _trusted_evidence_count_tuples(result.record) == [
        ("component-evidence.v1", "tdom-svcs.processor", "observed", 2),
    ]
```

- [ ] **Step 2: Run focused Pydantic parity test**

Run:

```bash
uv run pytest tests/test_pydantic_evals_adapter.py::test_run_pydantic_eval_suite_writes_grouped_component_evidence_records -q
```

Expected: PASS once Tasks 2 and 3 are complete.

- [ ] **Step 3: Run Pydantic adapter regression tests**

Run:

```bash
uv run pytest tests/test_pydantic_evals_adapter.py -q
```

Expected: PASS.

---

### Task 6: Final Verification and Roadmap Update

**Files:**
- Modify: `docs/superpowers/roadmap.md`
- Optional modify: `/Users/pauleveritt/projects/t-strings/tainie/docs/superpowers/roadmap.md`

- [ ] **Step 1: Run tdom-svcs verification**

Run from `/Users/pauleveritt/projects/t-strings/tdom-svcs`:

```bash
just quality
just test
```

Expected: PASS.

- [ ] **Step 2: Run Tainie verification**

Run from `/Users/pauleveritt/projects/t-strings/tainie`:

```bash
just quality
just test tests/test_eval_fixtures.py tests/test_evidence_providers.py tests/test_eval_runner.py tests/test_pydantic_evals_adapter.py
```

Expected: PASS.

- [ ] **Step 3: Confirm import discipline manually**

Run from `/Users/pauleveritt/projects/t-strings/tainie`:

```bash
uv run python - <<'PY'
import sys
import tainie.eval.evidence_providers

raise SystemExit("tdom_svcs imported") if "tdom_svcs" in sys.modules else None
PY
```

Expected: exits with code 0 and prints nothing.

- [ ] **Step 4: Update tdom-svcs roadmap item 47**

In `docs/superpowers/roadmap.md`, change item 47 from unchecked to checked only after verification passes:

```markdown
47. [x] P1 Tainie Component Evidence Provider Integration — Tainie's P3a-P5
```

Add a completion note under the item:

```markdown
    Completed 2026-05-06: `tdom-svcs` now projects component inspection packets
    into Tainie's trusted component evidence report shape, and Tainie can attach
    that evidence through an opt-in `component_provider` lane across native and
    Pydantic Evals entrypoints. Provider drift is quarantined, missing producers
    yield zero evidence, and Tainie imports stay free of `tdom_svcs` unless the
    caller opts into the component producer registration helper.
```

- [ ] **Step 5: Inspect the final diff**

Run:

```bash
git -C /Users/pauleveritt/projects/t-strings/tdom-svcs diff --stat
git -C /Users/pauleveritt/projects/t-strings/tainie diff --stat
```

Expected: only the files named in this plan changed, plus any pre-existing roadmap modifications the user already had.

- [ ] **Step 6: Report completion without committing**

Summarize:

- files changed in `tdom-svcs`;
- files changed in Tainie;
- verification commands and outcomes;
- any pre-existing dirty files that were left untouched.

Do not commit unless the user explicitly asks for a commit.

---

## Self-Review

### Spec Coverage

- Dedicated `component_provider` lane: Tasks 2 and 3.
- `tdom-svcs` owns component packet and a package-owned projection helper: Task 1.
- Tainie registry and registration helper: Task 3.
- Strict malformed-output quarantine through provider failure path: Tasks 3 and 4.
- Native eval entrypoint evidence: Task 4.
- Pydantic Evals parity: Task 5.
- No default Tainie import of `tdom_svcs`: Tasks 3 and 6.
- Rendered output unchanged: Task 1 limits `tdom-svcs` changes to projection only; Task 6 runs full tests.

### Placeholder Scan

The plan avoids red-flag placeholder instructions and includes concrete test and
implementation snippets for each code-changing task.

### Type Consistency

- Tainie fixture field is consistently named `component_provider`.
- Tainie registry is consistently named `COMPONENT_EVIDENCE_PRODUCERS`.
- Provider factory is consistently named `component_evidence_provider_for`.
- Projection adapter is consistently named `component_projection_to_report`.
- `tdom-svcs` projection helper is consistently named `component_evidence_packet_to_mapping`.
