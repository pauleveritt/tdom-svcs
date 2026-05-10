import json
from pathlib import Path
from typing import Any

import pytest
from sphinx.cmd.build import build_main


ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.filterwarnings(
    "ignore:.*MystReferenceResolver.app.*:sphinx.deprecation.RemovedInSphinx11Warning"
)


def test_docs_build_validates_and_exports_domain_inventory(tmp_path: Path) -> None:
    outdir = tmp_path / "html"
    doctreedir = tmp_path / "doctrees"

    result = build_main(
        [
            "-W",
            "-b",
            "html",
            "-d",
            str(doctreedir),
            str(ROOT / "docs"),
            str(outdir),
        ]
    )

    assert result == 0

    inventory_path = outdir / "domain-inventory.json"
    payload = json.loads(inventory_path.read_text())

    assert payload["schema_version"] == 1
    assert payload["validation_issues"] == []
    assert "domain/index" in payload["records_by_doc"]

    records = _records_by_id(payload)
    assert {
        "render-entry-point",
        "di-component-processor",
        "resource-context",
        "resource-marker",
        "component-di-flows-through-hopscotch",
        "tests-match-output-risk",
        "resource-field-witness",
        "component-evidence-packet",
        "component-evidence-packet-witness",
        "template-returning-component",
        "callable-component-shape",
        "component-tag-props",
        "component-default-argument",
        "component-type-hint",
        "component-children-template",
        "basic-components-return-template",
        "component-tags-pass-props",
        "component-body-content-flows-through-children",
        "pure-tdom-component-shape-witness",
        "component-flavors-witness",
        "component-children-witness",
    } <= records.keys()

    resource_marker = records["resource-marker"]
    assert resource_marker["fact_kind"] == "concept"
    assert resource_marker["status"] == "verified"
    assert resource_marker["target"]["kind"] == "symbol"
    assert resource_marker["target"]["resolved"] is True

    resource_witness = records["resource-field-witness"]
    assert resource_witness["fact_kind"] == "witness"
    assert resource_witness["target_reference"]["resolved"] is True
    assert "resource-shape-is-downstream-owned" in resource_witness["proves"]

    template_component = records["template-returning-component"]
    assert template_component["fact_kind"] == "concept"
    assert template_component["status"] == "verified"
    assert template_component["target"]["kind"] == "symbol"
    assert template_component["target"]["resolved"] is True

    pure_tdom_witness = records["pure-tdom-component-shape-witness"]
    assert pure_tdom_witness["fact_kind"] == "witness"
    assert pure_tdom_witness["target_reference"]["resolved"] is True
    assert "basic-components-return-template" in pure_tdom_witness["proves"]
    assert "component-tags-pass-props" in pure_tdom_witness["proves"]

    children_witness = records["component-children-witness"]
    assert children_witness["fact_kind"] == "witness"
    assert children_witness["target_reference"]["resolved"] is True
    assert "component-body-content-flows-through-children" in children_witness[
        "proves"
    ]
    assert "no-container-rendering-stays-plain" in children_witness["proves"]
    assert "component-di-flows-through-hopscotch" not in children_witness["proves"]


def _records_by_id(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {record["id"]: record for record in payload["records"]}
