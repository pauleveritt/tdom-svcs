"""Props priority and InitVar pattern.

This example demonstrates:

- Using InitVar to receive props from context
- Props explicitly passed override context values
- Dataclass fields with init=False and __post_init__
- How props take priority over injected dependencies
"""

from dataclasses import InitVar, dataclass

from svcs import Container, Registry
from svcs_di import Inject, auto
from tdom import Node

from examples.common import Database as BaseDatabase, Request, UserDict
from tdom_svcs import html


# A service that depends on the database
@dataclass
class Users:
    """Service that depends on Database."""

    request: Inject[Request]
    db: Inject[BaseDatabase]

    def get_current_user(self) -> UserDict:
        """Use the info on the container to get the current UserDict"""
        current_user_id = int(self.request.user_id)
        return self.db.users[current_user_id]

    def get_user(self, user_id: int) -> UserDict:
        """Get user by ID."""
        return self.db.users.get(
            user_id, {"id": user_id, "name": "Unknown", "role": "guest"}
        )

    def list_user(self) -> list[UserDict]:
        """List all users."""
        return list(self.db.users.values())


# A component that injects the Users service
@dataclass
class Greeting:
    """Greeting component that displays welcome message for current user."""

    users: InitVar[Inject[Users]]
    current_name: str | None = None

    def __post_init__(self, users: Users) -> None:
        if self.current_name is None:
            current_user = users.get_current_user()
            self.current_name = current_user["name"]

    def __call__(self) -> Node:
        return html(t"<h1>Hello {self.current_name}!</h1>")


def main() -> tuple[str, str]:
    # Set up the service registry
    registry = Registry()

    registry.register_factory(BaseDatabase, BaseDatabase)
    # User registration using auto(User) to wrap
    registry.register_factory(Users, auto(Users))

    with Container(registry) as container:
        # A request comes in, grab the user_id from the route and put
        # in the container.
        request = Request(user_id="1")
        container.register_local_value(Request, request)

        # Override the user_name prop from here in this call
        response1 = html(t'<{Greeting} current_name="Mary" />', context=container)
        result1 = str(response1)
        assert "Mary" in result1

        # Let the injector derive the value
        response2 = html(t"<{Greeting} />", context=container)
        result2 = str(response2)
        assert "Alice" in result2

        return result1, result2


if __name__ == "__main__":
    print(main())
