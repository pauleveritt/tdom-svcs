"""Services for the dependencies middleware example.

Re-exports common services and adds Logger and MetricsCollector
for middleware dependency injection demonstration.
"""

from dataclasses import dataclass, field

# Re-export common services
from examples.common.services import (
    DEFAULT_USERS,
    Database,
    UserDict,
    Users,
    UsersDict,
)

__all__ = [
    "Database",
    "DEFAULT_USERS",
    "Logger",
    "MetricsCollector",
    "UserDict",
    "Users",
    "UsersDict",
]


@dataclass
class Logger:
    """Logger service for middleware to use."""

    name: str
    messages: list[str] = field(default_factory=list)

    def info(self, message: str) -> None:
        """Log an info message."""
        self.messages.append(f"[{self.name}] INFO: {message}")

    def get_messages(self) -> list[str]:
        """Get all logged messages."""
        return self.messages.copy()


@dataclass
class MetricsCollector:
    """Metrics service for tracking component usage."""

    _metrics: dict[str, int] = field(default_factory=dict)

    def record(self, component_name: str) -> None:
        """Record a component being processed."""
        self._metrics[component_name] = self._metrics.get(component_name, 0) + 1

    def get_count(self, component_name: str) -> int:
        """Get the count for a specific component."""
        return self._metrics.get(component_name, 0)

    def get_all_metrics(self) -> dict[str, int]:
        """Get all metrics."""
        return self._metrics.copy()
