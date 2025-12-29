"""Card component with direct decorator application."""

from dataclasses import dataclass

from svcs_di.injectors.decorators import injectable


@dataclass
class Card:
    """
    A card component without @injectable decorator.

    We'll apply the decorator programmatically in app.py.
    """

    title: str = "Default Card"
    content: str = "Default content"

    def __call__(self) -> str:
        """Render the card."""
        return f"""
        <div class="card">
            <h3>{self.title}</h3>
            <p>{self.content}</p>
        </div>
        """.strip()


# Apply decorator directly (Example 4 from spec.md)
# Note: injectable() modifies the class in-place, no reassignment needed
injectable(Card)
