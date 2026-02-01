"""Services for the aria verifier example."""

from dataclasses import dataclass, field

from svcs_di.injectors import injectable


@injectable
@dataclass
class Logger:
    """Simple logging service that collects warnings.

    Used by AriaVerifierMiddleware to log accessibility violations.
    """

    warnings: list[str] = field(default_factory=list)

    def warn(self, message: str) -> None:
        """Log a warning message."""
        self.warnings.append(message)
