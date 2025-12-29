"""Button function component."""

from svcs_di import Inject

from basic_tdom_svcs.services.database import DatabaseService


def button(label: str, db: Inject[DatabaseService]) -> str:
    """
    Simple button function component with dependency injection.

    This is a function component - it cannot be registered by string name
    or discovered with @injectable. It must be called directly.

    Args:
        label: The button label text
        db: Injected database service (automatically provided by KeywordInjector)

    Returns:
        HTML string for the button
    """
    # Access injected database service
    user = db.get_user(1)

    return f'<button class="btn">{label} - User: {user["name"]}</button>'
