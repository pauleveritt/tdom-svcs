"""User card component."""

from dataclasses import dataclass

from svcs_di import Inject
from svcs_di.injectors.decorators import injectable

from basic_tdom_injectable.services.database import DatabaseService


@injectable
@dataclass
class UserCard:
    """
    User card component showing user information.

    This component demonstrates how to pass regular parameters along with
    injected dependencies.

    Args:
        user_id: Regular parameter provided by caller
        db: Injected database service (automatic)
    """

    user_id: int
    db: Inject[DatabaseService]

    def render(self) -> str:
        """
        Render the user card as HTML.

        Returns:
            HTML string for the user card
        """
        user = self.db.get_user(self.user_id)

        return f"""
        <div class="card">
            <div class="card-header">User Profile</div>
            <div class="card-body">
                <h5>{user["name"]}</h5>
                <p>Role: {user["role"]}</p>
                <p>Email: {user["email"]}</p>
            </div>
        </div>
        """

    def __call__(self) -> str:
        """Allow component to be called directly."""
        return self.render()
