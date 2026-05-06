"""Component flavors: functions, dataclasses, and POCOs.

This example demonstrates:

- Function components with explicit props
- Dataclass components with props
- POCO (Plain Old Class Object) components with __init__
- Props priority: explicit props override default values
"""

from dataclasses import dataclass
from string.templatelib import Template

from tdom_svcs import html


# docs: start dataclass-component
@dataclass
class Greeting2:
    name: str = "World"

    def __call__(self) -> Template:
        return t"<h1>Hello {self.name}!</h1>"


# docs: end dataclass-component


# docs: start poco-component
class Greeting3:
    def __init__(self, name: str = "World") -> None:
        self.name = name

    def __call__(self) -> Template:
        return t"<h1>Hello {self.name}!</h1>"


# docs: end poco-component


# docs: start function-component
def Greeting1(name: str = "World") -> Template:
    """Render a greeting."""
    return t"<h1>Hello {name}!</h1>"


# docs: end function-component


def main() -> tuple[str, str, str]:
    # docs: start render-function
    response1 = html(t"<{Greeting1} name='Alice' />")
    result1 = str(response1)
    assert "Alice" in result1
    # docs: end render-function

    # docs: start render-dataclass
    response2 = html(t"<{Greeting2} name='Alice' />")
    result2 = str(response2)
    assert "Alice" in result2
    # docs: end render-dataclass

    # docs: start render-poco
    response3 = html(t"<{Greeting3} name='Alice' />")
    result3 = str(response3)
    assert "Alice" in result3
    # docs: end render-poco

    return result1, result2, result3


if __name__ == "__main__":
    print(main())
