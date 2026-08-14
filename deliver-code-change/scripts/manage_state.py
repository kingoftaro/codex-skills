#!/usr/bin/env python3
"""Create and update one single-writer cross-session task-state JSON file atomically."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROUTES = ("Fast", "Standard", "High-risk")
STATUSES = ("in_progress", "completed")
REQUIRED_FIELDS = {
    "schema_version",
    "task_id",
    "route",
    "status",
    "current_step",
    "completed_steps",
    "changed_files",
    "verification",
    "resume_hint",
    "created_at",
    "updated_at",
}
STRING_FIELDS = ("task_id", "current_step", "resume_hint", "created_at", "updated_at")
STRING_LIST_FIELDS = ("completed_steps", "changed_files", "verification")


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def validate_state(data: dict[str, Any]) -> dict[str, Any]:
    missing = sorted(REQUIRED_FIELDS - set(data))
    if missing:
        raise ValueError(f"state is missing required fields: {missing}")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise ValueError(f"unsupported state schema_version: {data['schema_version']!r}")
    if data["route"] not in ROUTES:
        raise ValueError(f"invalid state route: {data['route']!r}")
    if data["status"] not in STATUSES:
        raise ValueError(f"invalid state status: {data['status']!r}")
    for field in STRING_FIELDS:
        if not isinstance(data[field], str) or (field != "resume_hint" and not data[field].strip()):
            raise ValueError(f"state field {field} must be a non-empty string")
    for field in STRING_LIST_FIELDS:
        value = data[field]
        if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
            raise ValueError(f"state field {field} must be an array of strings")
    for field in ("created_at", "updated_at"):
        try:
            parsed = datetime.fromisoformat(data[field])
        except ValueError as exc:
            raise ValueError(f"state field {field} must be an ISO-8601 timestamp") from exc
        if parsed.tzinfo is None:
            raise ValueError(f"state field {field} must include a timezone")
    if data["status"] == "completed" and data["current_step"] != "complete":
        raise ValueError("completed state must use current_step 'complete'")
    if data["status"] == "in_progress" and data["current_step"] == "complete":
        raise ValueError("in-progress state cannot use current_step 'complete'")
    return data


def load_state(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"state file does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in state file {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("state must be a JSON object")
    return validate_state(data)


def write_atomic(path: Path, state: dict[str, Any]) -> None:
    validate_state(state)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(state, indent=2, ensure_ascii=False) + "\n"
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def unique_append(values: list[str], additions: list[str]) -> list[str]:
    result = list(values)
    for item in additions:
        if item and item not in result:
            result.append(item)
    return result


def initialize(args: argparse.Namespace) -> dict[str, Any]:
    now = timestamp()
    return {
        "schema_version": 1,
        "task_id": args.task_id,
        "route": args.route,
        "status": "in_progress",
        "current_step": args.step,
        "completed_steps": [],
        "changed_files": [],
        "verification": [],
        "resume_hint": args.resume_hint,
        "created_at": now,
        "updated_at": now,
    }


def update(args: argparse.Namespace, complete_task: bool = False) -> dict[str, Any]:
    path = Path(args.file)
    state = load_state(path)
    if state["status"] == "completed":
        raise ValueError("completed state is immutable; initialize a new state file for new work")
    if args.step is not None:
        state["current_step"] = args.step
    state["completed_steps"] = unique_append(state.get("completed_steps", []), args.complete or [])
    state["changed_files"] = unique_append(state.get("changed_files", []), args.changed or [])
    state["verification"] = unique_append(state.get("verification", []), args.verification or [])
    if args.resume_hint is not None:
        state["resume_hint"] = args.resume_hint
    if complete_task:
        state["status"] = "completed"
        state["current_step"] = "complete"
    state["updated_at"] = timestamp()
    return validate_state(state)


def add_update_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--file", required=True)
    parser.add_argument("--step")
    parser.add_argument("--complete", action="append")
    parser.add_argument("--changed", action="append")
    parser.add_argument("--verification", action="append")
    parser.add_argument("--resume-hint")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    init_parser = commands.add_parser("init")
    init_parser.add_argument("--file", required=True)
    init_parser.add_argument("--task-id", required=True)
    init_parser.add_argument("--route", choices=ROUTES, required=True)
    init_parser.add_argument("--step", default="inspect")
    init_parser.add_argument("--resume-hint", default="")

    update_parser = commands.add_parser("update")
    add_update_arguments(update_parser)

    show_parser = commands.add_parser("show")
    show_parser.add_argument("--file", required=True)

    complete_parser = commands.add_parser("complete")
    add_update_arguments(complete_parser)

    args = parser.parse_args()
    path = Path(args.file)
    try:
        if args.command == "init":
            if path.exists():
                raise ValueError(f"state file already exists: {path}; inspect it before replacing")
            state = initialize(args)
            write_atomic(path, state)
        elif args.command == "update":
            state = update(args)
            write_atomic(path, state)
        elif args.command == "complete":
            if args.resume_hint is None:
                args.resume_hint = ""
            state = update(args, complete_task=True)
            write_atomic(path, state)
        else:
            state = load_state(path)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(state, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
