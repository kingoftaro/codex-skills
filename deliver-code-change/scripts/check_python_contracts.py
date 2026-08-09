#!/usr/bin/env python3
"""Compare explicit JSON interface contracts with Python source signatures."""

from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


KINDS = {"function", "method", "class"}


@dataclass(frozen=True)
class Symbol:
    qualified_name: str
    kind: str
    parameters: tuple[str, ...] = ()
    return_annotation: str | None = None
    is_async: bool | None = None
    file: str | None = None
    line: int | None = None


def normalized_annotation(node: ast.expr | None) -> str | None:
    if node is None:
        return None
    return "".join(ast.unparse(node).split())


def normalize_expected(value: str | None) -> str | None:
    return None if value is None else "".join(value.split())


def parameter_names(arguments: ast.arguments, drop_receiver: bool) -> tuple[str, ...]:
    names = [argument.arg for argument in (*arguments.posonlyargs, *arguments.args)]
    if drop_receiver and names and names[0] in {"self", "cls"}:
        names = names[1:]
    if arguments.vararg:
        names.append(f"*{arguments.vararg.arg}")
    names.extend(argument.arg for argument in arguments.kwonlyargs)
    if arguments.kwarg:
        names.append(f"**{arguments.kwarg.arg}")
    return tuple(names)


def module_name(path: Path, source_root: Path) -> str:
    relative = path.relative_to(source_root).with_suffix("")
    parts = list(relative.parts)
    if parts and parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def extract_symbols(source_root: Path) -> tuple[dict[str, list[Symbol]], list[str]]:
    found: dict[str, list[Symbol]] = {}
    failures: list[str] = []

    for path in sorted(source_root.rglob("*.py")):
        if any(part in {".git", ".venv", "venv", "__pycache__", "build", "dist"} for part in path.parts):
            continue
        try:
            content = path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(path))
        except (OSError, UnicodeError, SyntaxError) as exc:
            failures.append(f"SOURCE_PARSE_ERROR {path}: {exc}")
            continue

        module = module_name(path, source_root)

        def add(symbol: Symbol) -> None:
            found.setdefault(symbol.qualified_name, []).append(symbol)

        for node in tree.body:
            prefix = f"{module}." if module else ""
            if isinstance(node, ast.ClassDef):
                class_name = f"{prefix}{node.name}"
                add(Symbol(class_name, "class", file=str(path), line=node.lineno))
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        add(Symbol(
                            qualified_name=f"{class_name}.{item.name}",
                            kind="method",
                            parameters=parameter_names(item.args, drop_receiver=True),
                            return_annotation=normalized_annotation(item.returns),
                            is_async=isinstance(item, ast.AsyncFunctionDef),
                            file=str(path),
                            line=item.lineno,
                        ))
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                add(Symbol(
                    qualified_name=f"{prefix}{node.name}",
                    kind="function",
                    parameters=parameter_names(node.args, drop_receiver=False),
                    return_annotation=normalized_annotation(node.returns),
                    is_async=isinstance(node, ast.AsyncFunctionDef),
                    file=str(path),
                    line=node.lineno,
                ))
    return found, failures


def load_contract(path: Path) -> list[Symbol]:
    try:
        payload: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read contract {path}: {exc}") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("symbols"), list):
        raise ValueError("contract must be an object containing a symbols array")
    if not payload["symbols"]:
        raise ValueError("contract symbols array is empty; zero symbols cannot pass verification")

    symbols: list[Symbol] = []
    seen: set[str] = set()
    for index, item in enumerate(payload["symbols"]):
        if not isinstance(item, dict):
            raise ValueError(f"symbols[{index}] must be an object")
        name = item.get("qualified_name")
        kind = item.get("kind")
        parameters = item.get("parameters", [])
        annotation = item.get("return_annotation")
        async_value = item.get("async")
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"symbols[{index}].qualified_name must be a non-empty string")
        if name in seen:
            raise ValueError(f"duplicate contract symbol: {name}")
        seen.add(name)
        if kind not in KINDS:
            raise ValueError(f"symbols[{index}].kind must be one of {sorted(KINDS)}")
        if not isinstance(parameters, list) or any(not isinstance(value, str) for value in parameters):
            raise ValueError(f"symbols[{index}].parameters must be an array of strings")
        if annotation is not None and not isinstance(annotation, str):
            raise ValueError(f"symbols[{index}].return_annotation must be a string when present")
        if async_value is not None and not isinstance(async_value, bool):
            raise ValueError(f"symbols[{index}].async must be a boolean when present")
        if kind == "class" and (parameters or annotation is not None or async_value is not None):
            raise ValueError(f"class contract {name} cannot declare parameters, return_annotation, or async")
        symbols.append(Symbol(name, kind, tuple(parameters), normalize_expected(annotation), async_value))
    return symbols


def compare(expected: list[Symbol], actual: dict[str, list[Symbol]], parse_failures: list[str]) -> tuple[list[str], list[str]]:
    passed: list[str] = []
    failed = list(parse_failures)
    for contract in expected:
        matches = actual.get(contract.qualified_name, [])
        if not matches:
            failed.append(f"MISSING {contract.kind} {contract.qualified_name}")
            continue
        if len(matches) > 1:
            locations = ", ".join(f"{item.file}:{item.line}" for item in matches)
            failed.append(f"AMBIGUOUS {contract.qualified_name}: {locations}")
            continue
        source = matches[0]
        differences: list[str] = []
        if source.kind != contract.kind:
            differences.append(f"kind expected {contract.kind}, got {source.kind}")
        if contract.kind != "class" and source.parameters != contract.parameters:
            differences.append(f"parameters expected {list(contract.parameters)}, got {list(source.parameters)}")
        if contract.return_annotation is not None and source.return_annotation != contract.return_annotation:
            differences.append(f"return expected {contract.return_annotation!r}, got {source.return_annotation!r}")
        if contract.is_async is not None and source.is_async != contract.is_async:
            differences.append(f"async expected {contract.is_async}, got {source.is_async}")
        location = f"{source.file}:{source.line}"
        if differences:
            failed.append(f"MISMATCH {contract.qualified_name} at {location}: {'; '.join(differences)}")
        else:
            passed.append(f"PASS {contract.qualified_name} at {location}")
    return passed, failed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", required=True, help="structured contract JSON")
    parser.add_argument("--source-root", required=True, help="Python import root to scan")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()

    source_root = Path(args.source_root)
    if not source_root.is_dir():
        parser.error(f"source root is not a directory: {source_root}")
    try:
        expected = load_contract(Path(args.contract))
    except ValueError as exc:
        parser.error(str(exc))
    actual, parse_failures = extract_symbols(source_root)
    passed, failed = compare(expected, actual, parse_failures)
    result = {"passed": passed, "failed": failed, "summary": {"passed": len(passed), "failed": len(failed)}}
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        for line in passed:
            print(line)
        for line in failed:
            print(line, file=sys.stderr)
        print(f"Summary: {len(passed)} passed, {len(failed)} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
