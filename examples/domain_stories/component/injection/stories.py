"""Domain-aware stories for component injection behavior."""

from storyville import DomainStory, DomainSubject, Story, Subject

from examples.domain_stories.component.injection.components import (
    GreetingService,
    InjectedGreeting,
)


def this_subject() -> Subject:
    """Return stories that point at existing tdom-svcs domain rules."""
    return Subject(
        title="Injected Greeting",
        target=InjectedGreeting,
        domain=DomainSubject(
            concepts=[
                "render-entry-point",
                "injected-component-field",
            ],
            tags=["storyville", "tdom-svcs"],
        ),
        items=[
            Story(
                title="Template Value Wins",
                props={"greeting": GreetingService("Template")},
                domain=DomainStory(
                    status="verified",
                    role="canonical",
                    proves=[
                        "template-attributes-override-injection",
                        "tests-match-output-risk",
                    ],
                    tags=["template-kwargs", "injection"],
                ),
            ),
            Story(
                title="Missing Container Boundary",
                domain=DomainStory(
                    status="verified",
                    role="edge_case",
                    proves=["component-di-flows-through-hopscotch"],
                    against=["no-container-rendering-stays-plain"],
                    tags=["required-di", "boundary"],
                ),
            ),
        ],
    )
