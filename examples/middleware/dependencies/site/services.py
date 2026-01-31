"""Site-specific service fakes for testing.

Demonstrates the testing pattern of using simple fakes
instead of mock frameworks.
"""

from dataclasses import dataclass, field


@dataclass
class FakeLogger:
    """Fake logger for testing - captures messages without side effects.

    This is a simple fake that implements the same interface as Logger,
    but stores messages for later inspection in tests.
    """

    name: str
    messages: list[str] = field(default_factory=list)

    def info(self, message: str) -> None:
        """Log an info message (stores for inspection)."""
        self.messages.append(f"[{self.name}] INFO: {message}")

    def get_messages(self) -> list[str]:
        """Get all logged messages for test assertions."""
        return self.messages.copy()

    def clear(self) -> None:
        """Clear all logged messages."""
        self.messages.clear()
