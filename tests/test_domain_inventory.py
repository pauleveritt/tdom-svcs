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


def _records_by_id(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {record["id"]: record for record in payload["records"]}
