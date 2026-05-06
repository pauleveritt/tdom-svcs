"""Service-to-service injection with imperative registration.

This example demonstrates:

- Imperative service registration without decorators
- Using auto() wrapper for service-to-service injection
- Service dependencies resolved through the container
- Component injection with Inject[] markers
"""

from dataclasses import dataclass
from string.templatelib import Template

from svcs import Container, Registry
from svcs_di import Inject, auto

from examples.common import Database as BaseDatabase
from examples.common import Request, UserDict
from tdom_svcs import html


# A service that depends on the database
# docs: start users-service
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


# docs: end users-service


# A component that injects the Users service
# docs: start greeting-component
@dataclass
class Greeting:
    """Greeting component that displays welcome message for current user."""

    users: Inject[Users]

    def __call__(self) -> Template:
        current_user = self.users.get_current_user()
        return t"<h1>Hello {current_user['name']}!</h1>"


# docs: end greeting-component


def main() -> str:
    # docs: start registry-setup
    # Set up the service registry
    registry = Registry()

    registry.register_factory(BaseDatabase, BaseDatabase)
    # User registration using auto(User) to wrap
    registry.register_factory(Users, auto(Users))
    # docs: end registry-setup

    with Container(registry) as container:
        # docs: start request-context
        # A request comes in, grab the user_id from the route and put
        # in the container.
        request = Request(user_id="1")
        container.register_local_value(Request, request)
        # docs: end request-context

        # docs: start render-component
        # Dataclass component: pass context container into the rendering
        response = html(t"<{Greeting} />", container=container)
        result = str(response)
        assert "Alice" in result
        # docs: end render-component

        return result


if __name__ == "__main__":
    print(main())
