from dataclasses import dataclass
from typing import Any


@dataclass
class Greeting:
    """
    A simple greeting component that uses context data.
    """

    name: str = "World"

    def __call__(self) -> str:
        """Render a greeting message."""
        return f"<div class='greeting'>Hello, {self.name}!</div>"


@dataclass
class UserInfo:
    """
    A component that displays user information from context.
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
