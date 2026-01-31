"""Services and components that are builtin into an application."""
from dataclasses import dataclass, field
from typing import TypedDict

from svcs_di import Inject
from svcs_di.injectors import injectable, HopscotchRegistry, HopscotchContainer
from svcs_di.injectors.scanning import scan
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
@injectable
@dataclass
class Database:
    """Example database service that can be injected using Inject[Database]."""

    users: UsersDict = field(init=False)

    def __post_init__(self) -> None:
        """Populate the users key in the dict."""
        self.users = DEFAULT_USERS.copy()


# A service that depends on the database
@injectable
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

    users: Inject[Users]

    def __call__(self) -> Node:
        current_user = self.users.get_current_user()
        return html(t"<h1>Hello {current_user['name']}!</h1>")


def main() -> str:
    # Set up the service registry
    registry = HopscotchRegistry()

    # Auto-discover and register all @injectable classes
    scan(registry, locals_dict=globals())

    with HopscotchContainer(registry) as container:
        # A request comes in, grab the user_id from the route and put
        # in the container.
        request = Request(user_id="1")
        container.register_local_value(Request, request)

        # Dataclass component: pass context container into the rendering
        response = html(t"<{Greeting} />", context=container)
        result = str(response)
        assert "Alice" in result

        return result


if __name__ == "__main__":
    print(main())
