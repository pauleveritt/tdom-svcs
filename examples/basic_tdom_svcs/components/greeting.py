"""Greeting component."""

from tdom import Node
from tdom_svcs import html

from examples.basic_tdom_svcs.services.database import DatabaseService


def greeting(db: DatabaseService) -> Node:
    """
    A simple function component that receives a service.

    NOTE: KeywordInjector is used for this example.
    """
    users = db.list_users()
    user_count = len(users)
    return html(t"<div>Hello from tdom_svcs! (Users: {user_count})</div>")
