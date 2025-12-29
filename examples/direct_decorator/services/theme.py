"""Theme service for component styling."""


class ThemeService:
    """Service for theming."""

    def get_theme(self, context_type: str) -> str:
        themes = {
            "customer": "blue",
            "admin": "red",
            "default": "green",
        }
        return themes.get(context_type, "default")
