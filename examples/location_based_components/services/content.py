"""Content service for location-based components."""


class ContentService:
    """Mock content service."""

    def get_page_content(self, path: str) -> str:
        content_map = {
            "/": "Welcome to our site!",
            "/about": "About us page",
            "/contact": "Contact information",
        }
        return content_map.get(path, "Page not found")
