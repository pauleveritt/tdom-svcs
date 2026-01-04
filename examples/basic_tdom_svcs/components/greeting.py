"""Greeting component."""

from dataclasses import dataclass

from examples.basic_tdom_svcs.services.database import DatabaseService


def greeting(db: DatabaseService) -> str:
    """
    A simple function component that receives a service.

    NOTE: KeywordInjector is used for this example.
    """
    users = db.list_users()
    return f"<div>Hello from tdom_svcs! (Users: {len(users)})</div>"
