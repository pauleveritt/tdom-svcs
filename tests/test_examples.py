"""Tests that verify all examples work correctly."""

from __future__ import annotations

import asyncio
import importlib.util
import inspect
import sys
from pathlib import Path
from types import ModuleType

import pytest

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"


def _collect_dirs(root: Path, max_depth: int = 2) -> list[Path]:
    dirs = [root]
    level = [root]
    for _ in range(max_depth):
        level = sorted(sub for d in level for sub in d.iterdir() if sub.is_dir())
        dirs.extend(level)
    return dirs


def get_example_modules(
    examples_dir: Path,
    *,
    max_depth: int = 2,
    skip_prefixes: tuple[str, ...] = ("__", "test_"),
    module_root: Path | None = None,
) -> list[ModuleType]:
    """Import all example .py files found up to max_depth levels deep.

    If module_root is given, it is added to sys.path and used as the root for
    computing dotted module names. Use this when examples cross-import via
    'from <module_root_relative_path> import x'.
    """
    dirs = _collect_dirs(examples_dir, max_depth)
    name_root = module_root if module_root is not None else examples_dir

    if module_root is not None:
        if (s := str(module_root)) not in sys.path:
            sys.path.insert(0, s)
    else:
        for d in dirs:
            if (s := str(d)) not in sys.path:
                sys.path.insert(0, s)

    modules: list[ModuleType] = []
    for directory in dirs:
        for py_file in sorted(directory.glob("*.py")):
            if any(py_file.name.startswith(p) for p in skip_prefixes):
                continue
            module_name = ".".join(py_file.relative_to(name_root).with_suffix("").parts)
            spec = importlib.util.spec_from_file_location(module_name, py_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
                modules.append(module)
    return modules


@pytest.mark.parametrize(
    "example_module",
    get_example_modules(EXAMPLES_DIR),
    ids=lambda m: m.__name__,
)
def test_example_runs_without_error(example_module: ModuleType) -> None:
    if not hasattr(example_module, "main"):
        pytest.skip(f"No main() in {example_module.__name__}")
    main = example_module.main
    if inspect.iscoroutinefunction(main):
        asyncio.run(main())
    else:
        main()


# --- Tests for get_example_modules ---


def test_finds_root_level_file(tmp_path: Path) -> None:
    (tmp_path / "basic.py").write_text("def main(): pass\n")
    modules = get_example_modules(tmp_path)
    assert [m.__name__ for m in modules] == ["basic"]


def test_finds_nested_file(tmp_path: Path) -> None:
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "app.py").write_text("def main(): pass\n")
    modules = get_example_modules(tmp_path)
    assert [m.__name__ for m in modules] == ["sub.app"]


def test_skips_dunder_and_test_files(tmp_path: Path) -> None:
    (tmp_path / "__init__.py").write_text("")
    (tmp_path / "test_foo.py").write_text("def main(): pass\n")
    (tmp_path / "real.py").write_text("x = 1\n")
    modules = get_example_modules(tmp_path)
    assert [m.__name__ for m in modules] == ["real"]


def test_custom_skip_prefix(tmp_path: Path) -> None:
    (tmp_path / "check_layout.py").write_text("def main(): pass\n")
    (tmp_path / "basic.py").write_text("def main(): pass\n")
    modules = get_example_modules(tmp_path, skip_prefixes=("__", "test_", "check_"))
    assert [m.__name__ for m in modules] == ["basic"]


def test_respects_max_depth(tmp_path: Path) -> None:
    deep = tmp_path / "a" / "b" / "c"
    deep.mkdir(parents=True)
    (deep / "too_deep.py").write_text("x = 1\n")
    (tmp_path / "a" / "b" / "ok.py").write_text("x = 1\n")
    modules = get_example_modules(tmp_path, max_depth=2)
    assert [m.__name__ for m in modules] == ["a.b.ok"]


def test_module_root_uses_root_relative_names(tmp_path: Path) -> None:
    examples = tmp_path / "examples"
    examples.mkdir()
    sub = examples / "sub"
    sub.mkdir()
    (sub / "app.py").write_text("x = 1\n")
    modules = get_example_modules(examples, module_root=tmp_path)
    assert [m.__name__ for m in modules] == ["examples.sub.app"]
