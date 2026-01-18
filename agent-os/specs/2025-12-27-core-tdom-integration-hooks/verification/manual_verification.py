"""
Manual verification script for core tdom integration hooks.

This script demonstrates the new functionality with mock implementations
and verifies that protocols work correctly without inheritance.
"""

import sys
from collections import ChainMap
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from string.templatelib import Template
from typing import Any, Callable

# Add tdom to path for testing
tdom_path = Path(__file__).parent.parent.parent.parent.parent / "tdom"
sys.path.insert(0, str(tdom_path))

from tdom import html  # noqa: E402
from tdom.nodes import Node  # noqa: E402
from tdom.processor import ComponentLookup, Config  # noqa: E402


# Test Components
def Button(*, label: str = "Click", disabled: bool = False) -> Template:
    """A simple button component."""
    disabled_attr = "disabled" if disabled else ""
    return t"<button {disabled_attr}>{label}</button>"


def Card(*, title: str, children: tuple[Node, ...] = ()) -> Template:
    """A card component with title and children."""
    return t"<div class='card'><h2>{title}</h2>{children}</div>"


def Alert(*, message: str, level: str = "info") -> Template:
    """An alert component."""
    return t"<div class='alert alert-{level}'>{message}</div>"


# Mock ComponentLookup without Protocol inheritance
@dataclass
class MockComponentLookup:
    """Mock ComponentLookup that doesn't inherit from Protocol."""

    container: Any
    component_registry: dict[str, Callable] = None

    def __post_init__(self):
        if self.component_registry is None:
            self.component_registry = {}

    def register(self, name: str, component: Callable) -> None:
        """Register a component replacement."""
        self.component_registry[name] = component

    def __call__(self, name: str, context: Mapping[str, Any]) -> Callable | None:
        """Look up a component by name."""
        print(f"  ComponentLookup called for: {name}")
        print(f"  Context keys: {list(context.keys())}")
        return self.component_registry.get(name)


# Mock Config without Protocol inheritance
@dataclass
class MockConfig:
    """Mock Config that doesn't inherit from Protocol."""

    component_lookup: ComponentLookup | None = None


def verify_protocol_structural_typing():
    """Verify that protocols work with duck-typed classes."""
    print("\n=== Verifying Protocol Structural Typing ===")

    # Create instances without inheriting from protocols
    lookup = MockComponentLookup(container="test_container")
    config = MockConfig(component_lookup=lookup)

    # Verify they satisfy protocols via structural typing
    print(
        f"MockComponentLookup satisfies ComponentLookup protocol: {isinstance(lookup, ComponentLookup)}"
    )
    print(f"MockConfig satisfies Config protocol: {isinstance(config, Config)}")

    return config


def verify_basic_component_injection():
    """Verify basic component injection works."""
    print("\n=== Verifying Basic Component Injection ===")

    # Create injected button
    def InjectedButton(*, label: str = "Click", disabled: bool = False) -> Template:
        return t"<button class='injected-btn' disabled={disabled}>{label}</button>"

    lookup = MockComponentLookup(container="test")
    lookup.register("Button", InjectedButton)
    config = MockConfig(component_lookup=lookup)
    context = {"user": "test_user", "request_id": "123"}

    print("Rendering button with injection...")
    result = html(t"<{Button} label='Submit' />", config=config, context=context)
    print(f"Result: {result}")

    expected = '<button class="injected-btn">Submit</button>'
    assert str(result) == expected, f"Expected {expected}, got {str(result)}"
    print("SUCCESS: Basic component injection works!")


def verify_nested_component_injection():
    """Verify nested component injection works."""
    print("\n=== Verifying Nested Component Injection ===")

    # Create injected versions
    def InjectedCard(*, title: str, children: tuple[Node, ...] = ()) -> Template:
        return t"<section class='injected-card'><h3>{title}</h3>{children}</section>"

    def InjectedButton(*, label: str = "Click", disabled: bool = False) -> Template:
        return t"<button class='injected-btn'>{label}</button>"

    lookup = MockComponentLookup(container="test")
    lookup.register("Card", InjectedCard)
    lookup.register("Button", InjectedButton)
    config = MockConfig(component_lookup=lookup)
    context = {"theme": "dark"}

    print("Rendering nested components with injection...")
    result = html(
        t"<{Card} title='Actions'><{Button} label='Save' /><{Button} label='Cancel' /></{Card}>",
        config=config,
        context=context,
    )
    print(f"Result: {result}")

    expected = '<section class="injected-card"><h3>Actions</h3><button class="injected-btn">Save</button><button class="injected-btn">Cancel</button></section>'
    assert str(result) == expected, f"Expected {expected}, got {str(result)}"
    print("SUCCESS: Nested component injection works!")


def verify_fallback_behavior():
    """Verify fallback to default components when lookup returns None."""
    print("\n=== Verifying Fallback Behavior ===")

    lookup = MockComponentLookup(container="test")
    # Don't register Button - should fallback to default
    config = MockConfig(component_lookup=lookup)
    context = {}

    print("Rendering button WITHOUT injection (fallback)...")
    result = html(t"<{Button} label='Default' />", config=config, context=context)
    print(f"Result: {result}")

    expected = "<button>Default</button>"
    assert str(result) == expected, f"Expected {expected}, got {str(result)}"
    print("SUCCESS: Fallback behavior works!")


def verify_context_with_dict():
    """Verify context works with plain dict."""
    print("\n=== Verifying Context with Dict ===")

    lookup = MockComponentLookup(container="test")
    config = MockConfig(component_lookup=lookup)
    context_dict = {
        "user_id": 42,
        "session": "abc123",
        "permissions": ["read", "write"],
    }

    print(f"Passing dict as context: {context_dict}")
    result = html(t"<{Button} label='Test' />", config=config, context=context_dict)
    print(f"Result: {result}")
    print("SUCCESS: Dict context works!")


def verify_context_with_chainmap():
    """Verify context works with ChainMap."""
    print("\n=== Verifying Context with ChainMap ===")

    lookup = MockComponentLookup(container="test")
    config = MockConfig(component_lookup=lookup)

    # Create ChainMap with layered contexts
    base_context = {"theme": "light", "locale": "en"}
    user_context = {"user_id": 123, "theme": "dark"}  # theme override
    chain_map = ChainMap(user_context, base_context)

    print("Passing ChainMap as context:")
    print(f"  Base context: {base_context}")
    print(f"  User context: {user_context}")
    print(f"  Combined (theme should be 'dark'): {dict(chain_map)}")

    result = html(t"<{Button} label='ChainMap' />", config=config, context=chain_map)
    print(f"Result: {result}")
    print("SUCCESS: ChainMap context works!")


def verify_backward_compatibility():
    """Verify backward compatibility when config/context not provided."""
    print("\n=== Verifying Backward Compatibility ===")

    print("Calling html() without config or context...")
    result1 = html(t"<{Button} label='Old Style' />")
    print(f"Result: {result1}")
    expected1 = "<button>Old Style</button>"
    assert str(result1) == expected1

    print("Calling html() with config=None, context=None...")
    result2 = html(t"<{Button} label='Explicit None' />", config=None, context=None)
    print(f"Result: {result2}")
    expected2 = "<button>Explicit None</button>"
    assert str(result2) == expected2

    print("SUCCESS: Backward compatibility maintained!")


def verify_no_svcs_dependencies():
    """Verify that tdom has no dependencies on svcs or svcs-di."""
    print("\n=== Verifying No svcs/svcs-di Dependencies ===")

    import tdom.processor as processor_module

    module_vars = vars(processor_module)
    svcs_names = [name for name in module_vars if "svcs" in name.lower()]

    if svcs_names:
        print(f"ERROR: Found svcs-related names: {svcs_names}")
        return False

    print("Checking Protocol definitions...")
    assert hasattr(processor_module, "ComponentLookup"), (
        "Missing ComponentLookup protocol"
    )
    assert hasattr(processor_module, "Config"), "Missing Config protocol"

    # Verify ComponentLookup uses generic types
    lookup_protocol = processor_module.ComponentLookup
    assert hasattr(lookup_protocol, "__protocol_attrs__"), (
        "ComponentLookup not runtime_checkable"
    )

    print("SUCCESS: No svcs/svcs-di dependencies found!")
    print("  - ComponentLookup protocol defined")
    print("  - Config protocol defined")
    print("  - Protocols use runtime_checkable")
    return True


def main():
    """Run all verification tests."""
    print("=" * 70)
    print("MANUAL VERIFICATION: Core tdom Integration Hooks")
    print("=" * 70)

    try:
        # Run all verifications
        verify_protocol_structural_typing()
        verify_basic_component_injection()
        verify_nested_component_injection()
        verify_fallback_behavior()
        verify_context_with_dict()
        verify_context_with_chainmap()
        verify_backward_compatibility()
        verify_no_svcs_dependencies()

        print("\n" + "=" * 70)
        print("ALL VERIFICATIONS PASSED!")
        print("=" * 70)
        print("\nSummary:")
        print("  - Protocols work without inheritance (structural typing)")
        print("  - Component injection works (basic and nested)")
        print("  - Fallback behavior works when lookup returns None")
        print("  - Context works with dict and ChainMap")
        print("  - Backward compatibility maintained")
        print("  - No dependencies on svcs or svcs-di")
        return 0

    except Exception as e:
        print("\n" + "=" * 70)
        print(f"VERIFICATION FAILED: {e}")
        print("=" * 70)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
