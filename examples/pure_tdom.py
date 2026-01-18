from tdom import Node

from tdom_svcs import html


def Dashboard(context: dict[str, str] | None = None) -> Node:
    """A dashboard component that shows nested components with context."""
    user = context.get("user", "Unknown") if context else "Unknown"
    return html(t'<div class="dashboard">Hello {user}!</div>')


def main() -> str:
    """Demonstrate pure tdom usage with context dictionary."""
    context = {"user": "Alice"}
    response = html(t"<{Dashboard} />", context=context)
    result = str(response)
    assert "Alice" in result
    return result


if __name__ == "__main__":
    print(main())
