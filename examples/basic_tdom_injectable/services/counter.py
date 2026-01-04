"""Counter service for dependency injection."""

from dataclasses import dataclass

from svcs_di.injectors.decorators import injectable


@injectable
@dataclass
class Counter:
    count: int = 0
    name: str = "Basic Counter"
