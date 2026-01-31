"""Basic tdom-svcs with function component example.

Demonstrates passing an svcs.Container to html() as context,
which automatically injects Inject[] parameters into components.
"""

from dataclasses import dataclass, field
from typing import TypedDict

import svcs
from svcs_di import Inject, auto
from tdom import Node

from tdom_svcs import html


class UserDict(TypedDict):
    id: int
    name: str
    role: str


type Users = dict[int, UserDict]

DEFAULT_USERS: Users = {
    1: {"id": 1, "name": "Alice", "role": "admin"},
    2: {"id": 2, "name": "Bob", "role": "user"},
    3: {"id": 3, "name": "Charlie", "role": "guest"},
}


@dataclass
class Database:
    """Example database service that can be injected using Inject[Database]."""

    _users: Users = field(default_factory=lambda: DEFAULT_USERS.copy())

    def get_user(self, user_id: int) -> UserDict:
        """Get user by ID."""
        return self._users.get(
            user_id, {"id": user_id, "name": "Unknown", "role": "guest"}
        )

    def list_users(self) -> list[UserDict]:
        """List all users."""
        return list(self._users.values())

@dataclass
class Service:
    """A service that depends on a database."""

    db: Inject[Database]
    timeout: int = 30

def Greeting(service: Inject[Service]) -> Node:
    """A function component that receives an injected Database service."""
    users = service.db.list_users()
    timeout = service.timeout
    user_count = len(users)
    return html(t"<div>Hello! (Users: {user_count}, Timeout: {timeout})</div>")


def main() -> str:
    registry = svcs.Registry()
    registry.register_factory(Database, Database)
    # We use auto since the Service needs injection
    registry.register_factory(Service, auto(Service))

    # A request comes in
    with svcs.Container(registry) as container:
        # Pass container as context - html() auto-injects Inject[] params
        result = html(t"<main><{Greeting} /></main>", context=container)
        result = str(result)

        assert "Users: 3" in result
        assert "Timeout: 30" in result

        return result


if __name__ == "__main__":
    print(main())
