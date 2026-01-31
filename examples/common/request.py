"""Request type shared across examples."""

from dataclasses import dataclass


@dataclass
class Request:
    """Imagine a route of /user/{user_id}."""

    user_id: str
