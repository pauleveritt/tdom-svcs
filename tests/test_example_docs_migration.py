"""Guards for example docs migrated to tainie-tools example directives."""

from pathlib import Path

from tainie_tools.examples import scan_example_bundles, validate_example_inventory

ROOT = Path(__file__).resolve().parents[1]
DOC_EXAMPLES = ROOT / "docs" / "examples"
EXAMPLES = ROOT / "examples"


def test_example_docs_do_not_use_literalinclude_anchors() -> None:
    banned_patterns = ("```{literalinclude}", ":start-at:", ":end-at:")
    violations: list[str] = []

    for path in sorted(DOC_EXAMPLES.rglob("*.md")):
        lines = path.read_text(encoding="utf-8").splitlines()
        for line_number, line in enumerate(lines, start=1):
            if any(pattern in line for pattern in banned_patterns):
                relative = path.relative_to(ROOT)
                violations.append(f"{relative}:{line_number}: {line.strip()}")

    assert violations == [], "Found banned docs/example directives:\n" + "\n".join(
        violations
    )


def test_example_inventory_has_no_validation_issues() -> None:
    inventory = scan_example_bundles(EXAMPLES)
    issues = validate_example_inventory(inventory)

    assert [issue.message for issue in issues] == []
