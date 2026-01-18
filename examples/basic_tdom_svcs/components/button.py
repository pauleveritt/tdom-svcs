"""Interactive components."""

from tdom import Node
from tdom_svcs import html

from examples.basic_tdom_svcs.services.database import DatabaseService


def button(label: str, db: DatabaseService) -> Node:
    """
    A simple button component that receives a service.

    NOTE: KeywordInjector is used for this example.
    """
    status = db.get_status()
    return html(t"<button title='DB: {status}'>{label}</button>")
