"""Button component."""

from dataclasses import dataclass

from svcs_di.injectors.decorators import injectable


@injectable
@dataclass
class Button:
    """
    Simple button component with no dependencies.

    This component will be automatically discovered by scan_components()
    and registered as "Button" (derived from class.__name__).
    """

    label: str = "Click me"
    disabled: bool = False

    def __call__(self) -> str:
        """Render the button as HTML."""
        disabled_attr = " disabled" if self.disabled else ""
        return f"<button{disabled_attr}>{self.label}</button>"
