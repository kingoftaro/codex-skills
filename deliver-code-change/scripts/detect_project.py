#!/usr/bin/env python3
"""Inspect a repository without changing it and print a JSON capability summary."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path


LANGUAGE_MARKERS = {
    "python": ("pyproject.toml", "setup.py", "setup.cfg", "requirements.txt", "Pipfile"),
    "typescript-javascript": ("package.json", "tsconfig.json", "jsconfig.json"),
    "go": ("go.mod", "go.work"),
    "rust": ("Cargo.toml",),
}

TOOL_NAMES = (
    "git", "python", "python3", "pytest", "ruff", "mypy", "pyright",
    "uv", "poetry", "tox", "nox",
    "node", "npm", "pnpm", "yarn", "bun", "tsc", "eslint",
    "go", "gofmt", "cargo", "rustc",
)

IGNORED_DIRS = {
    ".git", ".hg", ".svn", ".tox", ".venv", "venv", "node_modules",
    "dist", "build", "target", "coverage", ".mypy_cache", ".pytest_cache",
    ".ruff_cache", "__pycache__",
}

SOURCE_SUFFIXES = {".py", ".pyi", ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".go", ".rs"}


def existing(root: Path, names: tuple[str, ...]) -> list[str]:
    return [name for name in names if (root / name).exists()]


def count_sources(root: Path) -> tuple[int, dict[str, int]]:
    total = 0
    suffixes: dict[str, int] = {}
    for current, directories, files in os.walk(root):
        directories[:] = [name for name in directories if name not in IGNORED_DIRS]
        for name in files:
            suffix = Path(name).suffix.lower()
            if suffix in SOURCE_SUFFIXES:
                total += 1
                suffixes[suffix] = suffixes.get(suffix, 0) + 1
    return total, dict(sorted(suffixes.items()))


def detect_package_manager(root: Path) -> str | None:
    for filename, manager in (
        ("pnpm-lock.yaml", "pnpm"),
        ("yarn.lock", "yarn"),
        ("bun.lockb", "bun"),
        ("bun.lock", "bun"),
        ("package-lock.json", "npm"),
    ):
        if (root / filename).exists():
            return manager
    return None


def detect_tools() -> dict[str, str | None]:
    tools = {name: shutil.which(name) for name in TOOL_NAMES}
    current_python = Path(sys.executable)
    if tools["python"] is None and current_python.is_file():
        tools["python"] = str(current_python.resolve())
    return tools


def inspect(root: Path) -> dict[str, object]:
    if not root.exists():
        raise FileNotFoundError(f"project root does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"project root is not a directory: {root}")

    languages = {
        language: existing(root, markers)
        for language, markers in LANGUAGE_MARKERS.items()
    }
    languages = {language: markers for language, markers in languages.items() if markers}
    source_count, source_suffixes = count_sources(root)
    if any(suffix in source_suffixes for suffix in (".py", ".pyi")):
        languages.setdefault("python", [])
    if any(suffix in source_suffixes for suffix in (".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx")):
        languages.setdefault("typescript-javascript", [])
    if ".go" in source_suffixes:
        languages.setdefault("go", [])
    if ".rs" in source_suffixes:
        languages.setdefault("rust", [])

    ci_markers = []
    for marker in (".github/workflows", ".gitlab-ci.yml", "azure-pipelines.yml", "Jenkinsfile"):
        if (root / marker).exists():
            ci_markers.append(marker)

    instruction_files = [
        name for name in ("AGENTS.md", "CLAUDE.md", "CONTRIBUTING.md")
        if (root / name).exists()
    ]

    return {
        "root": str(root.resolve()),
        "languages": languages,
        "package_manager": detect_package_manager(root),
        "source_files": {"total": source_count, "by_suffix": source_suffixes},
        "version_control": {"git": (root / ".git").exists()},
        "ci": ci_markers,
        "instructions": instruction_files,
        "openspec": (root / "openspec").exists(),
        "tools": detect_tools(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="repository root to inspect")
    args = parser.parse_args()
    try:
        result = inspect(Path(args.root))
    except (FileNotFoundError, NotADirectoryError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
