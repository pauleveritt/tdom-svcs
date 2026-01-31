"""Tests that verify all examples work correctly."""

import importlib.util
import inspect
import sys
from pathlib import Path
from types import ModuleType

import anyio
import pytest

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"

# Add examples directories to sys.path for imports (2 levels deep)
for path in EXAMPLES_DIR.iterdir():
    if path.is_dir():
        path_str = str(path)
        if path_str not in sys.path:
            sys.path.insert(0, path_str)
        # Also add second-level directories
        for subpath in path.iterdir():
            if subpath.is_dir():
                subpath_str = str(subpath)
                if subpath_str not in sys.path:
                    sys.path.insert(0, subpath_str)


def get_example_modules() -> list[ModuleType]:
    """Get all Python example files as imported modules, including up to 2 levels of subdirectories."""
    modules: list[ModuleType] = []

    # Build list of directories to search: examples dir + up to 2 levels of subdirectories
    dirs_to_search = [EXAMPLES_DIR]
    for first_level in sorted(p for p in EXAMPLES_DIR.iterdir() if p.is_dir()):
        dirs_to_search.append(first_level)
        # Add second-level subdirectories
        dirs_to_search.extend(sorted(p for p in first_level.iterdir() if p.is_dir()))

    # Import all .py files from all directories
    for directory in dirs_to_search:
        for py_file in sorted(directory.glob("*.py")):
            # Skip __init__.py and test files
            if py_file.name.startswith("__") or py_file.name.startswith("test_"):
                continue

            # Build module name based on directory depth relative to EXAMPLES_DIR
            rel_path = directory.relative_to(EXAMPLES_DIR)
            if rel_path == Path("."):
                module_name = py_file.stem
            else:
                module_name = f"{'.'.join(rel_path.parts)}.{py_file.stem}"

            spec = importlib.util.spec_from_file_location(module_name, py_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                modules.append(module)

    return modules


@pytest.mark.parametrize("example_module", get_example_modules())
def test_example_runs_without_error(example_module):
    """Test that each example runs without errors."""
    # Check if module has a main function
    if not hasattr(example_module, "main"):
        pytest.skip(f"Module {example_module.__name__} has no main function")

    main_func = getattr(example_module, "main")

    # Check if main is async
    if inspect.iscoroutinefunction(main_func):
        # Run async main
        anyio.run(main_func)
    else:
        # Run sync main
        main_func()
