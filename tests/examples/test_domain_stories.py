"""Tests for Storyville domain stories examples."""

from pathlib import Path

from storyville import collect_domain_evidence, make_catalog


def test_domain_stories_catalog_discovers_storyville_example() -> None:
    catalog = make_catalog("examples.domain_stories")

    assert catalog.title == "tdom-svcs Domain Stories"
    assert "component" in catalog.items
    assert "injection" in catalog.items["component"].items


def test_domain_stories_collect_domain_evidence() -> None:
    records = collect_domain_evidence("examples.domain_stories")

    assert records == [
        {
            "kind": "story",
            "package_location": "examples.domain_stories",
            "section_path": ".component",
            "subject_path": ".component.injection",
            "story_path": ".component.injection.0",
            "section_title": "Component Evidence",
            "subject_title": "Injected Greeting",
            "story_title": "Template Value Wins",
            "resource_path": "component/injection/0",
            "subject_domain": {
                "concepts": [
                    "render-entry-point",
                    "injected-component-field",
                ],
                "tags": ["storyville", "tdom-svcs"],
            },
            "story_domain": {
                "status": "verified",
                "role": "canonical",
                "proves": [
                    "template-attributes-override-injection",
                    "tests-match-output-risk",
                ],
                "against": [],
                "tags": ["template-kwargs", "injection"],
            },
        },
        {
            "kind": "story",
            "package_location": "examples.domain_stories",
            "section_path": ".component",
            "subject_path": ".component.injection",
            "story_path": ".component.injection.1",
            "section_title": "Component Evidence",
            "subject_title": "Injected Greeting",
            "story_title": "Missing Container Boundary",
            "resource_path": "component/injection/1",
            "subject_domain": {
                "concepts": [
                    "render-entry-point",
                    "injected-component-field",
                ],
                "tags": ["storyville", "tdom-svcs"],
            },
            "story_domain": {
                "status": "verified",
                "role": "edge_case",
                "proves": ["component-di-flows-through-hopscotch"],
                "against": ["no-container-rendering-stays-plain"],
                "tags": ["required-di", "boundary"],
            },
        },
    ]


def test_domain_story_rule_ids_exist_in_domain_source() -> None:
    domain_source = Path("docs/domain/index.md").read_text()
    records = collect_domain_evidence("examples.domain_stories")

    referenced_ids = {
        rule_id
        for record in records
        for rule_id in (
            record["story_domain"]["proves"] + record["story_domain"]["against"]
        )
    }

    for rule_id in referenced_ids:
        assert f":id: {rule_id}" in domain_source
