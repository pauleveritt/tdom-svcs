from dataclasses import dataclass
from typing import Any, Callable
from examples.pure_tdom.components import Greeting, UserInfo, Dashboard


@dataclass
class SimpleConfig:
    """
    Simple configuration object with just a component_lookup.
    """

    component_lookup: Callable[[str, dict[str, Any]], Callable | None] | None = None


def simple_component_lookup(name: str, context: dict[str, Any]) -> Callable | None:
    """
    Simple component lookup that returns component classes by name.
    """
    components = {
        "Greeting": Greeting,
        "UserInfo": UserInfo,
        "Dashboard": Dashboard,
    }
    return components.get(name)


def svcs_setup(config: SimpleConfig):
    """
    In this pure example, we just attach the lookup to the config.
    """
    config.component_lookup = simple_component_lookup
