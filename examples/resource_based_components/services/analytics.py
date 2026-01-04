"""Analytics service for tracking user behavior."""


class AnalyticsService:
    """Mock analytics service."""

    def get_stats(self) -> dict[str, int]:
        return {"visits": 42, "conversions": 5}
