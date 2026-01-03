"""Pytest configuration for docs/ markdown doctests.

This conftest handles docs/**/*.md only (README.md is in root conftest.py)
Uses PythonCodeBlockParser to parse ```python blocks containing doctest syntax.
"""

from sybil import Sybil
from sybil.parsers.myst import PythonCodeBlockParser


# Configure Sybil for docs/ markdown files
pytest_collect_file = Sybil(
    parsers=[PythonCodeBlockParser()],
    patterns=["*.md"],
    path=".",
    setup=lambda ns: ns.update(
        {
            # Common imports for documentation examples
            "svcs": __import__("svcs"),
            "dataclasses": __import__("dataclasses"),
            "Inject": __import__("svcs_di").Inject,
            "injectable": __import__("svcs_di.injectors.decorators").injectors.decorators.injectable,
            "HopscotchInjector": __import__("svcs_di.injectors.locator").injectors.locator.HopscotchInjector,
            "HopscotchAsyncInjector": __import__("svcs_di.injectors.locator").injectors.locator.HopscotchAsyncInjector,
            "ComponentNameRegistry": __import__("tdom_svcs").ComponentNameRegistry,
            "scan_components": __import__("tdom_svcs").scan_components,
            "ComponentLookup": __import__("tdom_svcs.services.component_lookup").services.component_lookup.ComponentLookup,
        }
    ),
).pytest()
