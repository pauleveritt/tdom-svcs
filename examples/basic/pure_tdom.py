"""Pure tdom with props parameter fundamentals.

This example demonstrates:

- Basic function component rendering without DI framework
- Function components receiving props as parameters
- Foundation pattern used throughout tdom-svcs
"""

from markupsafe import Markup

from tdom_svcs import html


def Greeting(name: str = "World") -> str | Markup:
    """Render a greeting with the given name."""
    return html(t"<h1>Hello {name}!</h1>")


def main() -> str:
    response = html(t"<{Greeting} name='Alice' />")

    result = str(response)
    assert "Alice" in result

    return result


if __name__ == "__main__":
    print(main())
