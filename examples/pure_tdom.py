"""
Example: Pure tdom with Config and Context Dictionaries

This example demonstrates the simplest possible usage of tdom-svcs where
config and context are just plain dictionaries, with no svcs container or
dependency injection framework involved.

NOTE: This example shows the conceptual pattern for how config and context
work with components. The components manually receive and use the context
dictionary, demonstrating how data can be passed down through the component tree.

This shows:
1. Creating a simple Config object with a component_lookup function
2. Passing a context dictionary with data
3. Components that can access the context to render dynamic content
4. No svcs, no @injectable decorators, no container - just pure tdom
5. How context flows from parent to child components
"""

from dataclasses import dataclass
from typing import Any, Callable

from tdom_svcs import html


# Step 1: Define simple component classes that can receive context
@dataclass
class Greeting:
    """
    A simple greeting component that uses context data.

    This component expects a 'context' parameter containing user information.
    """

    name: str = "World"

    def __call__(self) -> str:
        """Render a greeting message."""
        return f"<div class='greeting'>Hello, {self.name}!</div>"


@dataclass
class UserInfo:
    """
    A component that displays user information from context.

    This demonstrates how components can access the context dictionary
    to get runtime data.
    """

    context: dict[str, Any]

    def __call__(self) -> str:
        """Render user information from context."""
        user = self.context.get("user", {})
        name = user.get("name", "Anonymous")
        role = user.get("role", "guest")

        return f"""
        <div class="user-info">
            <h2>{name}</h2>
            <p>Role: {role}</p>
        </div>
        """


@dataclass
class Dashboard:
    """
    A dashboard component that shows nested components with context.
    """

    context: dict[str, Any]

    def __call__(self) -> str:
        """Render a dashboard with user info and greeting."""
        user = self.context.get("user", {})
        name = user.get("name", "Guest")

        # Create nested components, passing context down
        greeting = Greeting(name=name)
        user_info = UserInfo(context=self.context)

        return f"""
        <div class="dashboard">
            <header>{greeting()}</header>
            <main>{user_info()}</main>
        </div>
        """


# Step 2: Create a simple component lookup function
def simple_component_lookup(name: str, context: dict[str, Any]) -> Callable | None:
    """
    Simple component lookup that returns component classes by name.

    This is the simplest possible ComponentLookup - just a function that
    maps string names to component classes. No framework needed.

    Args:
        name: The component name to look up
        context: The context dictionary (passed but not used in this simple example)

    Returns:
        The component class if found, None otherwise
    """
    components = {
        "Greeting": Greeting,
        "UserInfo": UserInfo,
        "Dashboard": Dashboard,
    }
    return components.get(name)


# Step 3: Create a simple Config object
@dataclass
class SimpleConfig:
    """
    Simple configuration object with just a component_lookup.

    This satisfies the Config protocol required by tdom-svcs.html()
    but doesn't require any framework or container.
    """

    component_lookup: Callable[[str, dict[str, Any]], Callable | None] | None = None


def main():
    """Demonstrate pure tdom usage with config and context dictionaries."""

    # Create a context dictionary with user data
    context = {
        "user": {
            "name": "Alice",
            "role": "admin",
            "email": "alice@example.com",
        },
        "settings": {
            "theme": "dark",
            "language": "en",
        },
    }

    # Create a simple config with our component lookup function
    config = SimpleConfig(component_lookup=simple_component_lookup)

    # Example 1: Simple greeting using context data
    print("Example 1: Simple Greeting")
    print("-" * 40)
    greeting = Greeting(name=context["user"]["name"])
    print(greeting())
    print()

    # Example 2: User info component with full context
    print("Example 2: User Info with Context")
    print("-" * 40)
    user_info = UserInfo(context=context)
    print(user_info())
    print()

    # Example 3: Dashboard with nested components
    print("Example 3: Dashboard with Nested Components")
    print("-" * 40)
    dashboard = Dashboard(context=context)
    print(dashboard())
    print()

    # Example 4: Using different context
    print("Example 4: Different Context")
    print("-" * 40)
    different_context = {
        "user": {
            "name": "Bob",
            "role": "user",
        }
    }
    dashboard2 = Dashboard(context=different_context)
    print(dashboard2())
    print()

    print("✅ All examples completed!")
    print()
    print("Key Points:")
    print("- Config is just a dataclass with a component_lookup function")
    print("- Context is just a plain dictionary")
    print("- Components are simple classes that receive context")
    print("- No svcs container or DI framework required")
    print("- Components can pass context down to nested components")


if __name__ == "__main__":
    main()
