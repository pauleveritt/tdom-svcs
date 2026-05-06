"""Pure tdom with props parameter fundamentals.

This example demonstrates:

- Basic function component rendering without DI framework
- Function components receiving props as parameters
- Foundation pattern used throughout tdom-svcs
"""

from string.templatelib import Template

from tdom_svcs import html


# docs: start greeting-component
def Greeting(name: str = "World") -> Template:
    """Render a greeting with the given name."""
    return t"<h1>Hello {name}!</h1>"


# docs: end greeting-component


# docs: start render-call
def main() -> str:
    response = html(t"<{Greeting} name='Alice' />")

    result = str(response)
    assert "Alice" in result

    return result


# docs: end render-call


if __name__ == "__main__":
    print(main())
