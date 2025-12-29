"""Button component."""

from dataclasses import dataclass

from svcs_di import Inject
from svcs_di.injectors.decorators import injectable

from basic_tdom_injectable.services.database import DatabaseService


@injectable
@dataclass
class Button:
    """
    Simple button component with dependency injection.

    This component demonstrates:
    - @injectable decorator for automatic discovery
    - Inject[] for service dependencies
    - Component registration by string name ("Button")
    - Resolution via ComponentLookup

    The component will be automatically discovered by scan_components()
    and registered in ComponentNameRegistry as "Button".
    """

    label: str
    db: Inject[DatabaseService]  # Injected dependency

    def render(self) -> str:
        """
        Render the button as HTML.

        Returns:
            HTML string for the button
        """
        # Access injected database service
        user = self.db.get_user(1)

        return f'<button class="btn btn-primary">{self.label} - User: {user["name"]}</button>'

    def __call__(self) -> str:
        """Allow component to be called directly."""
        return self.render()
