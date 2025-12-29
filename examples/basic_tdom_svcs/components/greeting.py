"""Greeting function component."""

from svcs_di import Inject

from basic_tdom_svcs.services.database import DatabaseService


def greeting(user_id: int, db: Inject[DatabaseService]) -> str:
    """
    Greeting function component that shows user information.

    Args:
        user_id: The ID of the user to greet
        db: Injected database service

    Returns:
        HTML string with greeting
    """
    user = db.get_user(user_id)
    return f'<div class="greeting">Hello, {user["name"]}! (Role: {user["role"]})</div>'
