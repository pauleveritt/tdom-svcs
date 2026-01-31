"""Services shared across examples."""

from dataclasses import dataclass, field
from typing import TypedDict

from svcs_di import Inject
from svcs_di.injectors import injectable

from examples.common.request import Request


class UserDict(TypedDict):
    """Type definition for user data."""

    id: int
    name: str
    role: str


type UsersDict = dict[int, UserDict]

DEFAULT_USERS: UsersDict = {
    1: {"id": 1, "name": "Alice", "role": "admin"},
    2: {"id": 2, "name": "Bob", "role": "user"},
    3: {"id": 3, "name": "Charlie", "role": "guest"},
}


@injectable
@dataclass
class Database:
    """Example database service that can be injected using Inject[Database]."""

    users: UsersDict = field(init=False)

    def __post_init__(self) -> None:
        """Populate the users key in the dict."""
        self.users = DEFAULT_USERS.copy()


@injectable
@dataclass
class Users:
    """Service that depends on Database."""

    request: Inject[Request]
    db: Inject[Database]

    def get_current_user(self) -> UserDict:
        """Use the info on the container to get the current UserDict."""
        current_user_id = int(self.request.user_id)
        return self.db.users[current_user_id]

    def get_user(self, user_id: int) -> UserDict:
        """Get user by ID."""
        return self.db.users.get(
            user_id, {"id": user_id, "name": "Unknown", "role": "guest"}
        )

    def list_users(self) -> list[UserDict]:
        """List all users."""
        return list(self.db.users.values())
