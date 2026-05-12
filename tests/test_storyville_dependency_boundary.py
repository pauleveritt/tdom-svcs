"""Storyville dependency boundary tests."""

import ast
import tomllib
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _imports_storyville(path: Path) -> bool:
    """Return whether a Python file imports Storyville."""
    tree = ast.parse(path.read_text(), filename=str(path))
    for node in ast.walk(tree):
        match node:
            case ast.Import(names=names):
                if any(alias.name == "storyville" for alias in names):
                    return True
            case ast.ImportFrom(module=module) if module is not None:
                if module == "storyville" or module.startswith("storyville."):
                    return True
    return False


def test_storyville_is_dev_only() -> None:
    """tdom-svcs examples may use Storyville, but runtime code should not."""
    pyproject = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text())

    assert "storyville" not in pyproject["project"]["dependencies"]
    assert "storyville" in pyproject["dependency-groups"]["dev"]


def test_tdom_svcs_runtime_code_does_not_import_storyville() -> None:
    """Storyville imports are allowed in examples/tests, not src/tdom_svcs."""
    src_files = sorted((PROJECT_ROOT / "src" / "tdom_svcs").rglob("*.py"))

    offenders = [
        path.relative_to(PROJECT_ROOT).as_posix()
        for path in src_files
        if _imports_storyville(path)
    ]

    assert offenders == []
