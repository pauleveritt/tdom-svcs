"""Widget components with conditional decoration."""

from dataclasses import dataclass

from svcs_di.injectors.decorators import injectable


class FeatureFlags:
    """Feature flag configuration."""

    enable_analytics = True
    enable_reporting = False


@dataclass
class AnalyticsWidget:
    """Analytics widget component."""

    title: str = "Analytics"

    def __call__(self) -> str:
        return "<div>Analytics: 100 visitors today</div>"


@dataclass
class ReportingWidget:
    """Reporting widget component."""

    title: str = "Reports"

    def __call__(self) -> str:
        return "<div>Reports: 5 new reports</div>"


# Conditionally apply decorator based on feature flags
# Note: injectable() modifies the class in-place, no reassignment needed
flags = FeatureFlags()

if flags.enable_analytics:
    injectable(AnalyticsWidget)

if flags.enable_reporting:
    injectable(ReportingWidget)
