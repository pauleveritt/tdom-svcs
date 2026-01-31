from tdom import Node

from tdom_svcs import html


def Greeting(context: dict[str, str]) -> Node:
    """Use the request context to grab some info."""
    user = context.get("user", "Unknown")
    return html(t"<h1>Hello {user}!</h1>")


def main() -> str:
    # A request comes in, let's get some data as "context"
    context = {"user": "Alice"}

    # Now pass it into the rendering
    response = html(t"<{Greeting} />", context=context)

    # Check the result to make sure it has what we expect
    result = str(response)
    assert "Alice" in result

    return result


if __name__ == "__main__":
    print(main())
