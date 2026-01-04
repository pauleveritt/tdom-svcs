"""Interactive components."""

from dataclasses import dataclass

from examples.basic_tdom_svcs.services.database import DatabaseService


def button(label: str, db: DatabaseService) -> str:
    """
    A simple button component that receives a service.

    NOTE: KeywordInjector is used for this example.
    """
    status = db.get_status()
    return f"<button title='DB: {status}'>{label}</button>"
