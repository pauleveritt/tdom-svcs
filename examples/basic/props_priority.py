"""Inject a service into a service with svcs_di.auto"""

from dataclasses import InitVar, dataclass, field
from typing import TypedDict

from svcs import Container, Registry
from svcs_di import Inject, auto
from tdom import Node

from tdom_svcs import html


@dataclass
class Request:
    """Imagine a route of /user/{user_id}"""

    user_id: str


class UserDict(TypedDict):
    id: int
    name: str
    role: str


type UsersDict = dict[int, UserDict]

DEFAULT_USERS: UsersDict = {
    1: {"id": 1, "name": "Alice", "role": "admin"},
    2: {"id": 2, "name": "Bob", "role": "user"},
    3: {"id": 3, "name": "Charlie", "role": "guest"},
}


# The underlying service
@dataclass
class Database:
    """Example database service that can be injected using Inject[Database]."""

    users: UsersDict = field(init=False)

    def __post_init__(self) -> None:
        """Populate the users key in the dict."""
        self.users = DEFAULT_USERS.copy()


# A service that depends on the database
@dataclass
class Users:
    """Service that depends on Database."""

    request: Inject[Request]
    db: Inject[Database]

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

    registry.register_factory(Database, Database)
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
