# Tainie Evidence Live Container And Inventory Pilot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Harden the existing `tdom-svcs` component evidence path with a real live-container Tainie test, then make `tdom-svcs` a passive producer-inventory fixture for Tainie's DomainSpec/DomainPack compiler work.

**Architecture:** Keep `tdom-svcs` as the producer of detailed component and inventory artifacts. Tainie remains the consumer: it validates producer artifacts into trusted evidence packets, counts each evidence lane distinctly, and does not import Sphinx or producer docs at runtime. The first slice deliberately uses passive local artifacts and Storyville records; it does not replace Tainie's existing hand-written DomainPack prompt renderers.

**Tech Stack:** Python 3.14, pytest, Pydantic v2, uv, Ruff, ty, `tdom-svcs`, `svcs-di`, `svcs-hopscotch`, Storyville, Tainie evidence providers.

---

## File Structure

### Already Completed Before This Plan

- Modify: `docs/superpowers/roadmap.md`
  - Renumber Phase 13 from duplicate item `51` to item `52`.

### Live Container Evidence Hardening

- Modify: `/Users/pauleveritt/projects/t-strings/tainie/tests/test_evidence_providers.py`
  - Add one end-to-end test that constructs a real `HopscotchContainer`, calls `tdom_svcs.processor.inspect_component_evidence_packet()`, and lets Tainie's component provider convert it into `ComponentEvidenceReport`.

### Producer Inventory Evidence Pilot

- Modify: `/Users/pauleveritt/projects/t-strings/tainie/src/tainie/domain/decision_evidence.py`
  - Add `InventoryEvidenceReport` and include it in `TrustedEvidencePacket`.
- Modify: `/Users/pauleveritt/projects/t-strings/tainie/src/tainie/domain/__init__.py`
  - Export the new inventory evidence model.
- Modify: `/Users/pauleveritt/projects/t-strings/tainie/src/tainie/domain/domain_pack.py`
  - Add a small loader that reads `tdom-svcs` domain inventory, example inventory, Storyville domain stories, and existing hard-written Tainie pack JSONs as passive evidence.
- Modify: `/Users/pauleveritt/projects/t-strings/tainie/tests/test_domain_pack.py`
  - Prove the loader returns separate trusted evidence packets for domain inventory, example inventory, Storyville witnesses, and compiled pack evidence.
- Modify: `/Users/pauleveritt/projects/t-strings/tainie/tests/test_decision_evidence.py`
  - Prove `trusted_evidence_count_key()` supports the new packet.
- Modify: `/Users/pauleveritt/projects/t-strings/tainie/tests/test_eval_metrics.py`
  - Prove grouped metrics distinguish inventory evidence lanes from existing component provider evidence.
- Modify: `docs/superpowers/roadmap.md`
  - Mark the backlog live-container hardening sub-item complete after verification.
  - Mark item 52 complete only after the inventory pilot verification passes.

## Task 0: Roadmap Numbering Cleanup

**Files:**
- Modify: `docs/superpowers/roadmap.md`

- [x] **Step 1: Renumber the duplicate Phase 13 item**

Change the Phase 13 item heading from:

```markdown
51. [ ] P1 DomainSpec Inventory Pilot For Tainie
```

to:

```markdown
52. [ ] P1 DomainSpec Inventory Pilot For Tainie
```

- [ ] **Step 2: Verify item numbers around Phase 12 and Phase 13**

Run:

```bash
rg -n "^5[0-9]\. \\[" docs/superpowers/roadmap.md
```

Expected: Phase 12 contains item `50` and item `51`, then Phase 13 contains item `52`.

## Task 1: Add Live Container Component Evidence Test In Tainie

**Files:**
- Modify: `/Users/pauleveritt/projects/t-strings/tainie/tests/test_evidence_providers.py`

- [ ] **Step 1: Add the live-container provider regression test**

Add this test near `test_component_projection_to_report_uses_real_tdom_svcs_serializer`:

```python
def test_component_provider_uses_real_tdom_svcs_live_container_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    processor = pytest.importorskip("tdom_svcs.processor")
    svcs_di = pytest.importorskip("svcs_di")
    hopscotch = pytest.importorskip("svcs_hopscotch.injectors")

    @dataclass
    class Settings:
        label: str = "injected"

    @dataclass
    class Card:
        settings: svcs_di.Inject[Settings]

    @dataclass
    class CardOverride:
        settings: svcs_di.Inject[Settings]
        title: str = "Default"

    registry = hopscotch.HopscotchRegistry()
    registry.register_value(Settings, Settings())
    registry.register_implementation(Card, CardOverride)

    def producer(fixture: EvalFixture, workspace: Path) -> object:
        del fixture, workspace
        with hopscotch.HopscotchContainer(registry) as container:
            return processor.inspect_component_evidence_packet(
                container,
                Card,
                {"title": "Live"},
            )

    monkeypatch.setitem(
        COMPONENT_EVIDENCE_PRODUCERS,
        "live-tdom-svcs",
        producer,
    )
    fixture = _fixture(tmp_path, component_provider="live-tdom-svcs")

    provider = component_evidence_provider_for(fixture)

    assert provider is not None
    packets = provider(fixture, tmp_path / "workspace")
    assert len(packets) == 1
    report = packets[0]
    assert isinstance(report, ComponentEvidenceReport)
    assert report.schema_version == "component-evidence.v1"
    assert report.source == "tdom-svcs.processor"
    assert report.status == "observed"
    assert report.component.endswith(".Card")
    assert any(item.endswith(".CardOverride") for item in report.evidence)
    assert "implementation_swapped=true" in report.evidence
    assert "field:settings:injected-dependency" in report.evidence
    assert "field:title:template-attr" in report.evidence
```

- [ ] **Step 2: Run the focused test**

Run from `/Users/pauleveritt/projects/t-strings/tainie`:

```bash
uv run pytest tests/test_evidence_providers.py::test_component_provider_uses_real_tdom_svcs_live_container_path -q
```

Expected: PASS if the existing provider path is already sufficient. If it fails, the failure should identify a real drift between Tainie's provider conversion and `tdom-svcs` live packet production.

- [ ] **Step 3: Run the nearby provider tests**

Run from `/Users/pauleveritt/projects/t-strings/tainie`:

```bash
uv run pytest tests/test_evidence_providers.py -q
```

Expected: PASS.

- [ ] **Step 4: Run lint and type checks for the touched file**

Run from `/Users/pauleveritt/projects/t-strings/tainie`:

```bash
uv run ruff check tests/test_evidence_providers.py
uv run ruff format --check tests/test_evidence_providers.py
uv run ty check tests/test_evidence_providers.py
```

Expected: all commands pass.

- [ ] **Step 5: Review checkpoint**

Run from `/Users/pauleveritt/projects/t-strings/tainie`:

```bash
git diff -- tests/test_evidence_providers.py
```

Expected: only the live-container provider test has been added. Do not commit unless the user explicitly asks.

## Task 2: Add Inventory Evidence Packet Model

**Files:**
- Modify: `/Users/pauleveritt/projects/t-strings/tainie/src/tainie/domain/decision_evidence.py`
- Modify: `/Users/pauleveritt/projects/t-strings/tainie/src/tainie/domain/__init__.py`
- Modify: `/Users/pauleveritt/projects/t-strings/tainie/tests/test_decision_evidence.py`

- [ ] **Step 1: Add a failing count-key test**

In `/Users/pauleveritt/projects/t-strings/tainie/tests/test_decision_evidence.py`, update imports:

```python
from tainie.domain.decision_evidence import (
    ComponentEvidenceReport,
    InventoryEvidenceReport,
    RouteInspectionArtifact,
    RouteInspectionError,
    RouteInspectionReport,
    load_route_inspection_artifact,
    report_route_inspection,
    trusted_evidence_count_key,
)
```

Add this test near `test_trusted_evidence_count_key_supports_route_reports`:

```python
def test_trusted_evidence_count_key_supports_inventory_reports() -> None:
    report = InventoryEvidenceReport(
        schema_version="producer-inventory.v1",
        source="tdom-svcs.domain-inventory",
        status="loaded",
        producer_package="tdom-svcs",
        inventory_kind="domain-inventory",
        artifact_path="docs/_build/html/domain-inventory.json",
        item_count=12,
        evidence=[
            "record:component-evidence-packet:concept:verified",
            "record:component-di-flows-through-hopscotch:rule:verified",
        ],
    )

    assert trusted_evidence_count_key(report) == (
        "producer-inventory.v1",
        "tdom-svcs.domain-inventory",
        "loaded",
    )
```

- [ ] **Step 2: Run the focused failing test**

Run from `/Users/pauleveritt/projects/t-strings/tainie`:

```bash
uv run pytest tests/test_decision_evidence.py::test_trusted_evidence_count_key_supports_inventory_reports -q
```

Expected: FAIL because `InventoryEvidenceReport` is not defined yet.

- [ ] **Step 3: Add the inventory evidence model**

In `/Users/pauleveritt/projects/t-strings/tainie/src/tainie/domain/decision_evidence.py`, add these type aliases after `type ComponentEvidenceStatus`:

```python
type InventoryEvidenceStatus = Literal["loaded"]
type InventoryEvidenceKind = Literal[
    "domain-inventory",
    "example-inventory",
    "storyville-witness",
    "component-provider",
    "compiled-pack",
]
```

Add this model after `ComponentEvidenceReport`:

```python
class InventoryEvidenceReport(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    schema_version: Literal["producer-inventory.v1"]
    source: str
    status: InventoryEvidenceStatus
    producer_package: str
    inventory_kind: InventoryEvidenceKind
    artifact_path: str
    item_count: int
    evidence: list[str]
```

Replace the `TrustedEvidencePacket` alias with:

```python
type TrustedEvidencePacket = (
    RouteInspectionReport | ComponentEvidenceReport | InventoryEvidenceReport
)
```

- [ ] **Step 4: Export the model**

In `/Users/pauleveritt/projects/t-strings/tainie/src/tainie/domain/__init__.py`, add `InventoryEvidenceReport` to the import and `__all__` list:

```python
from tainie.domain.decision_evidence import (
    ComponentEvidenceReport,
    InventoryEvidenceReport,
    RouteInspectionArtifact,
    RouteInspectionError,
    RouteInspectionReport,
    TrustedEvidenceCountKey,
    TrustedEvidencePacket,
    load_route_inspection_artifact,
    report_route_inspection,
    trusted_evidence_count_key,
)
```

- [ ] **Step 5: Run the focused test again**

Run from `/Users/pauleveritt/projects/t-strings/tainie`:

```bash
uv run pytest tests/test_decision_evidence.py::test_trusted_evidence_count_key_supports_inventory_reports -q
```

Expected: PASS.

## Task 3: Load tdom-svcs Producer Inventories As Passive Evidence

**Files:**
- Modify: `/Users/pauleveritt/projects/t-strings/tainie/src/tainie/domain/domain_pack.py`
- Modify: `/Users/pauleveritt/projects/t-strings/tainie/tests/test_domain_pack.py`

- [ ] **Step 1: Add failing producer inventory loader tests**

In `/Users/pauleveritt/projects/t-strings/tainie/tests/test_domain_pack.py`, update imports:

```python
from tainie.domain.domain_pack import (
    DomainPackError,
    load_tdom_svcs_canonical_component_shape_pack,
    load_tdom_svcs_producer_inventory_evidence,
    load_tdom_svcs_props_priority_pack,
    load_tdom_svcs_service_injection_shape_pack,
    load_themester_layout_layering_pack,
    render_tdom_svcs_canonical_component_shape_prompt_evidence,
    render_tdom_svcs_props_priority_prompt_evidence,
    render_tdom_svcs_service_injection_shape_prompt_evidence,
    render_themester_layout_layering_prompt_evidence,
)
```

Add this test near the existing tdom-svcs pack tests:

```python
def test_load_tdom_svcs_producer_inventory_evidence_reads_passive_artifacts(
    tmp_path: Path,
) -> None:
    producer_root = tmp_path / "tdom-svcs"
    inventory_dir = producer_root / "docs" / "_build" / "html"
    inventory_dir.mkdir(parents=True)
    (inventory_dir / "domain-inventory.json").write_text(
        """
        {
          "records": [
            {
              "id": "component-evidence-packet",
              "fact_kind": "concept",
              "status": "verified",
              "source_path": "domain/index",
              "source_line": 142
            },
            {
              "id": "component-di-flows-through-hopscotch",
              "fact_kind": "rule",
              "status": "verified",
              "source_path": "domain/index",
              "source_line": 192
            }
          ],
          "validation_issues": []
        }
        """,
        encoding="utf-8",
    )
    (inventory_dir / "example-inventory.json").write_text(
        """
        {
          "bundles": [
            {
              "id": "basic/inject_service",
              "entrypoint": "basic/inject_service.py",
              "files": [{"path": "basic/inject_service.py"}],
              "proves": ["component-di-flows-through-hopscotch"]
            }
          ],
          "validation_issues": []
        }
        """,
        encoding="utf-8",
    )

    reports = load_tdom_svcs_producer_inventory_evidence(producer_root=producer_root)

    assert [(report.source, report.inventory_kind) for report in reports] == [
        ("tdom-svcs.domain-inventory", "domain-inventory"),
        ("tdom-svcs.example-inventory", "example-inventory"),
        ("tdom-svcs.storyville-witness", "storyville-witness"),
        ("tdom-svcs.compiled-pack", "compiled-pack"),
    ]
    assert reports[0].item_count == 2
    assert reports[0].evidence == [
        "record:component-evidence-packet:concept:verified",
        "record:component-di-flows-through-hopscotch:rule:verified",
    ]
    assert reports[1].item_count == 1
    assert reports[1].evidence == [
        "bundle:basic/inject_service:basic/inject_service.py"
    ]
    assert reports[2].item_count == 0
    assert reports[2].evidence == ["storyville=not-discovered"]
    assert reports[3].item_count == 3
    assert reports[3].evidence == [
        "pack:tdom-svcs.props-priority",
        "pack:tdom-svcs.canonical-component-shape",
        "pack:tdom-svcs.service-injection-shape",
    ]
```

- [ ] **Step 2: Run the focused failing test**

Run from `/Users/pauleveritt/projects/t-strings/tainie`:

```bash
uv run pytest tests/test_domain_pack.py::test_load_tdom_svcs_producer_inventory_evidence_reads_passive_artifacts -q
```

Expected: FAIL because `load_tdom_svcs_producer_inventory_evidence` is not defined yet.

- [ ] **Step 3: Add the passive inventory loader**

In `/Users/pauleveritt/projects/t-strings/tainie/src/tainie/domain/domain_pack.py`, add imports:

```python
from collections.abc import Iterator
from contextlib import contextmanager
import sys

from tainie.domain.decision_evidence import InventoryEvidenceReport
```

Add these helpers before `_list_of_mappings`:

```python
def load_tdom_svcs_producer_inventory_evidence(
    *,
    producer_root: Path,
) -> list[InventoryEvidenceReport]:
    """Read tdom-svcs producer artifacts as passive trusted evidence."""
    return [
        _domain_inventory_report(producer_root),
        _example_inventory_report(producer_root),
        _storyville_inventory_report(producer_root),
        _compiled_pack_inventory_report(),
    ]


def _domain_inventory_report(producer_root: Path) -> InventoryEvidenceReport:
    artifact_path = producer_root / "docs" / "_build" / "html" / "domain-inventory.json"
    payload = _load_json_mapping(artifact_path, blocker="domain_inventory_invalid_json")
    records = _list_of_mappings(payload, "records")
    return InventoryEvidenceReport(
        schema_version="producer-inventory.v1",
        source="tdom-svcs.domain-inventory",
        status="loaded",
        producer_package="tdom-svcs",
        inventory_kind="domain-inventory",
        artifact_path=str(artifact_path),
        item_count=len(records),
        evidence=[
            (
                f"record:{record.get('id', '')}:"
                f"{record.get('fact_kind', '')}:"
                f"{record.get('status', '')}"
            )
            for record in records
        ],
    )


def _example_inventory_report(producer_root: Path) -> InventoryEvidenceReport:
    artifact_path = producer_root / "docs" / "_build" / "html" / "example-inventory.json"
    payload = _load_json_mapping(artifact_path, blocker="example_inventory_invalid_json")
    bundles = _list_of_mappings(payload, "bundles")
    return InventoryEvidenceReport(
        schema_version="producer-inventory.v1",
        source="tdom-svcs.example-inventory",
        status="loaded",
        producer_package="tdom-svcs",
        inventory_kind="example-inventory",
        artifact_path=str(artifact_path),
        item_count=len(bundles),
        evidence=[
            f"bundle:{bundle.get('id', '')}:{bundle.get('entrypoint', '')}"
            for bundle in bundles
        ],
    )


def _storyville_inventory_report(producer_root: Path) -> InventoryEvidenceReport:
    artifact_path = producer_root / "examples" / "domain_stories"
    records = _collect_tdom_svcs_storyville_records(producer_root)
    evidence = (
        [
            (
                f"story:{record.get('resource_path', '')}:"
                f"{record.get('story_domain', {}).get('status', '')}:"
                f"{record.get('story_domain', {}).get('role', '')}"
            )
            for record in records
        ]
        if records
        else ["storyville=not-discovered"]
    )
    return InventoryEvidenceReport(
        schema_version="producer-inventory.v1",
        source="tdom-svcs.storyville-witness",
        status="loaded",
        producer_package="tdom-svcs",
        inventory_kind="storyville-witness",
        artifact_path=str(artifact_path),
        item_count=len(records),
        evidence=evidence,
    )


def _compiled_pack_inventory_report() -> InventoryEvidenceReport:
    packs = [
        TDOM_SVCS_PROPS_PRIORITY_PACK_ID,
        TDOM_SVCS_CANONICAL_COMPONENT_SHAPE_PACK_ID,
        TDOM_SVCS_SERVICE_INJECTION_SHAPE_PACK_ID,
    ]
    return InventoryEvidenceReport(
        schema_version="producer-inventory.v1",
        source="tdom-svcs.compiled-pack",
        status="loaded",
        producer_package="tdom-svcs",
        inventory_kind="compiled-pack",
        artifact_path="docs/domain/packs",
        item_count=len(packs),
        evidence=[f"pack:{pack_id}" for pack_id in packs],
    )


def _collect_tdom_svcs_storyville_records(
    producer_root: Path,
) -> list[DomainPackMapping]:
    try:
        from storyville import collect_domain_evidence
    except ModuleNotFoundError:
        return []
    with _prepend_sys_path(producer_root):
        return list(collect_domain_evidence("examples.domain_stories"))


@contextmanager
def _prepend_sys_path(path: Path) -> Iterator[None]:
    path_text = str(path)
    sys.path.insert(0, path_text)
    try:
        yield
    finally:
        try:
            sys.path.remove(path_text)
        except ValueError:
            pass


def _load_json_mapping(path: Path, *, blocker: str) -> DomainPackMapping:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise DomainPackError("producer_inventory_not_found") from exc
    except json.JSONDecodeError as exc:
        raise DomainPackError(blocker) from exc
    if not isinstance(payload, dict):
        raise DomainPackError("producer_inventory_not_object")
    return payload
```

- [ ] **Step 4: Run the focused test again**

Run from `/Users/pauleveritt/projects/t-strings/tainie`:

```bash
uv run pytest tests/test_domain_pack.py::test_load_tdom_svcs_producer_inventory_evidence_reads_passive_artifacts -q
```

Expected: PASS.

- [ ] **Step 5: Add a real tdom-svcs artifact smoke test**

Add this test in `/Users/pauleveritt/projects/t-strings/tainie/tests/test_domain_pack.py`:

```python
def test_load_tdom_svcs_producer_inventory_evidence_reads_real_tdom_svcs_build() -> None:
    producer_root = Path("/Users/pauleveritt/projects/t-strings/tdom-svcs")
    reports = load_tdom_svcs_producer_inventory_evidence(producer_root=producer_root)

    assert {report.source for report in reports} == {
        "tdom-svcs.domain-inventory",
        "tdom-svcs.example-inventory",
        "tdom-svcs.storyville-witness",
        "tdom-svcs.compiled-pack",
    }
    assert reports[0].item_count > 0
    assert reports[1].item_count > 0
    assert reports[2].item_count >= 2
    assert reports[3].item_count == 3
```

- [ ] **Step 6: Run the real artifact smoke test**

Run from `/Users/pauleveritt/projects/t-strings/tainie`:

```bash
uv run pytest tests/test_domain_pack.py::test_load_tdom_svcs_producer_inventory_evidence_reads_real_tdom_svcs_build -q
```

Expected: PASS after `tdom-svcs` docs have generated `docs/_build/html/domain-inventory.json` and `docs/_build/html/example-inventory.json`.

## Task 4: Prove Metrics Distinguish Inventory Lanes

**Files:**
- Modify: `/Users/pauleveritt/projects/t-strings/tainie/tests/test_eval_metrics.py`

- [ ] **Step 1: Add a grouped metrics test**

In `/Users/pauleveritt/projects/t-strings/tainie/tests/test_eval_metrics.py`, add `InventoryEvidenceReport` to the existing decision-evidence imports:

```python
from tainie.domain.decision_evidence import (
    ComponentEvidenceReport,
    InventoryEvidenceReport,
    RouteInspectionReport,
)
```

Add this test near `test_new_run_group_record_summarizes_trusted_evidence_counts`:

```python
def test_new_run_group_record_distinguishes_producer_inventory_evidence(
    tmp_path: Path,
) -> None:
    readiness = EvalReadiness(
        model_id="Qwen3-8B",
        provider_url="http://example.test/v1",
    )
    record = new_run_record(
        suite="evidence_canary",
        readiness=readiness,
        git_sha="abc123",
        warnings=[],
        fixtures=[
            _fixture_result("inventory_fixture", accepted=True).model_copy(
                update={
                    "trusted_evidence": [
                        InventoryEvidenceReport(
                            schema_version="producer-inventory.v1",
                            source="tdom-svcs.domain-inventory",
                            status="loaded",
                            producer_package="tdom-svcs",
                            inventory_kind="domain-inventory",
                            artifact_path="docs/_build/html/domain-inventory.json",
                            item_count=12,
                            evidence=[
                                "record:component-evidence-packet:concept:verified"
                            ],
                        ),
                        InventoryEvidenceReport(
                            schema_version="producer-inventory.v1",
                            source="tdom-svcs.example-inventory",
                            status="loaded",
                            producer_package="tdom-svcs",
                            inventory_kind="example-inventory",
                            artifact_path="docs/_build/html/example-inventory.json",
                            item_count=9,
                            evidence=[
                                "bundle:basic/inject_service:basic/inject_service.py"
                            ],
                        ),
                        InventoryEvidenceReport(
                            schema_version="producer-inventory.v1",
                            source="tdom-svcs.storyville-witness",
                            status="loaded",
                            producer_package="tdom-svcs",
                            inventory_kind="storyville-witness",
                            artifact_path="examples/domain_stories",
                            item_count=2,
                            evidence=["story:component/injection/0:verified:canonical"],
                        ),
                        ComponentEvidenceReport(
                            schema_version="component-evidence.v1",
                            source="tdom-svcs.processor",
                            status="observed",
                            component="tests.Card",
                            evidence=["requested=tests.Card"],
                        ),
                        InventoryEvidenceReport(
                            schema_version="producer-inventory.v1",
                            source="tdom-svcs.compiled-pack",
                            status="loaded",
                            producer_package="tdom-svcs",
                            inventory_kind="compiled-pack",
                            artifact_path="docs/domain/packs",
                            item_count=3,
                            evidence=["pack:tdom-svcs.props-priority"],
                        ),
                    ]
                }
            )
        ],
        run_group_id="20260509T120000Z-abc123-evidence_canary-1x",
        trial_index=1,
        trial_count=1,
    )

    group = metrics.new_run_group_record(
        run_group_id="20260509T120000Z-abc123-evidence_canary-1x",
        suite="evidence_canary",
        readiness=readiness,
        git_sha="abc123",
        trials=[record],
    )
    del tmp_path

    assert [
        (count.schema_version, count.source, count.status, count.count)
        for count in group.trusted_evidence_counts
    ] == [
        ("component-evidence.v1", "tdom-svcs.processor", "observed", 1),
        ("producer-inventory.v1", "tdom-svcs.compiled-pack", "loaded", 1),
        ("producer-inventory.v1", "tdom-svcs.domain-inventory", "loaded", 1),
        ("producer-inventory.v1", "tdom-svcs.example-inventory", "loaded", 1),
        ("producer-inventory.v1", "tdom-svcs.storyville-witness", "loaded", 1),
    ]
```

- [ ] **Step 2: Run the focused metrics test**

Run from `/Users/pauleveritt/projects/t-strings/tainie`:

```bash
uv run pytest tests/test_eval_metrics.py::test_new_run_group_record_distinguishes_producer_inventory_evidence -q
```

Expected: PASS.

## Task 5: Final Verification And Roadmap Updates

**Files:**
- Modify: `docs/superpowers/roadmap.md`

- [ ] **Step 1: Run tdom-svcs inventory verification**

Run from `/Users/pauleveritt/projects/t-strings/tdom-svcs`:

```bash
uv run pytest tests/test_domain_inventory.py tests/test_example_docs_migration.py tests/examples/test_domain_stories.py tests/test_judge_confidence_evidence.py -q
uv run sphinx-build -b html docs docs/_build/html -W
```

Expected: all commands pass and the docs build refreshes `docs/_build/html/domain-inventory.json` and `docs/_build/html/example-inventory.json`.

- [ ] **Step 2: Run Tainie verification**

Run from `/Users/pauleveritt/projects/t-strings/tainie`:

```bash
uv run pytest tests/test_evidence_providers.py tests/test_decision_evidence.py tests/test_domain_pack.py tests/test_eval_metrics.py -q
uv run ruff check src/tainie/domain/decision_evidence.py src/tainie/domain/__init__.py src/tainie/domain/domain_pack.py tests/test_evidence_providers.py tests/test_decision_evidence.py tests/test_domain_pack.py tests/test_eval_metrics.py
uv run ruff format --check src/tainie/domain/decision_evidence.py src/tainie/domain/__init__.py src/tainie/domain/domain_pack.py tests/test_evidence_providers.py tests/test_decision_evidence.py tests/test_domain_pack.py tests/test_eval_metrics.py
uv run ty check src/tainie/domain/decision_evidence.py src/tainie/domain/__init__.py src/tainie/domain/domain_pack.py tests/test_evidence_providers.py tests/test_decision_evidence.py tests/test_domain_pack.py tests/test_eval_metrics.py
```

Expected: all commands pass.

- [ ] **Step 3: Mark the live-container backlog sub-item complete**

In `docs/superpowers/roadmap.md`, update the backlog item that starts with:

```markdown
- [ ] Hygiene fixes from 2026-05-08 deep-dive audit
```

Keep the parent backlog item unchecked unless all three hygiene sub-items are done, but change clause `(c)` to state:

```markdown
(c) Completed 2026-05-09: Tainie now exercises
`inspect_component_evidence_packet()` against a live `HopscotchContainer`
through the registered `component_provider` path, so the component evidence
contract is pinned end-to-end.
```

- [ ] **Step 4: Mark roadmap item 52 complete**

In `docs/superpowers/roadmap.md`, change item 52 from unchecked to checked and add this completion note:

```markdown
    Completed 2026-05-09: Tainie now reads `tdom-svcs` domain inventory,
    example inventory, Storyville domain story records, and the three existing
    tdom-svcs DomainPack JSON files as distinct passive trusted evidence lanes.
    Metrics distinguish producer inventory evidence from component provider
    evidence, and `tdom-svcs` remains the authored source of truth for package
    domain facts.
```

- [ ] **Step 5: Review final diffs without committing**

Run:

```bash
git -C /Users/pauleveritt/projects/t-strings/tdom-svcs diff -- docs/superpowers/roadmap.md
git -C /Users/pauleveritt/projects/t-strings/tdom-svcs status --short docs/superpowers/plans/2026-05-09-tainie-evidence-live-container-and-inventory-pilot.md
git -C /Users/pauleveritt/projects/t-strings/tainie diff --stat
```

Expected: `tdom-svcs` has the roadmap update and this plan file; Tainie changes are limited to the files named above. Do not commit unless the user explicitly asks.

## Self-Review

### Spec Coverage

- Duplicate item `51` cleanup: Task 0.
- Live-container Tainie component evidence hardening: Task 1.
- Passive domain and example inventory evidence: Tasks 2 and 3.
- Storyville witness evidence: Task 3.
- Existing compiled pack evidence: Task 3.
- Metrics distinguish evidence lanes: Task 4.
- Roadmap completion and verification: Task 5.

### Placeholder Scan

The plan contains concrete file paths, code snippets, commands, and expected results. It avoids open-ended implementation instructions.

### Type Consistency

The new model is consistently named `InventoryEvidenceReport`. Its schema is `producer-inventory.v1`, and its lane discriminator is `inventory_kind`. Existing Tainie `ComponentEvidenceReport` remains the component provider evidence lane.
