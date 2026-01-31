from dataclasses import InitVar, dataclass, field
from typing import TypedDict

from tdom import Node

from tdom_svcs import html


class MyContext(TypedDict):
    user: str


@dataclass
class Greeting2:
    user: str = field(init=False)
    context: InitVar[MyContext]

    def __post_init__(self, context: MyContext) -> None:
        self.user = context["user"]

    def __call__(self) -> Node:
        return html(t"<h1>Hello {self.user}!</h1>")


class Greeting3:
    context: MyContext
    user: str

    def __init__(self, context: MyContext) -> None:
        self.context = context
        self.user = context["user"]

    def __call__(self) -> Node:
        return html(t"<h1>Hello {self.user}!</h1>")


def Greeting1(context: MyContext) -> Node:
    """Use the request context to grab some info."""
    user = context.get("user", "Unknown")
    return html(t"<h1>Hello {user}!</h1>")


def main() -> tuple[str, str, str]:
    # A request comes in, let's get some data as "context"
    context = {"user": "Alice"}

    # Function component: pass context into the rendering
    response1 = html(t"<{Greeting1} />", context=context)
    result1 = str(response1)
    assert "Alice" in result1

    # Dataclass component: pass context into the rendering
    response2 = html(t"<{Greeting2} />", context=context)
    result2 = str(response2)
    assert "Alice" in result2

    # Class component: pass context into the rendering
    response3 = html(t"<{Greeting3} />", context=context)
    result3 = str(response3)
    assert "Alice" in result3

    return result1, result2, result3


if __name__ == "__main__":
    print(main())
