#!/usr/bin/env python3
"""Create and update one cross-session task-state JSON file atomically."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROUTES = ("Fast", "Standard", "High-risk")
STATUSES = ("in_progress", "completed")
SCHEMA_VERSION = 1
STATE_KEYS = {
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


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_utc_timestamp(value: Any, label: str, errors: list[str]) -> datetime | None:
    if not isinstance(value, str) or not value:
        errors.append(f"{label} must be a non-empty UTC ISO 8601 string")
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        errors.append(f"{label} must be valid UTC ISO 8601")
        return None
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        errors.append(f"{label} must use UTC offset +00:00")
        return None
    return parsed


def validate_string_list(value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append(f"{label} must be a list")
        return
    valid_items = all(isinstance(item, str) and item for item in value)
    if not valid_items:
        errors.append(f"{label} must contain only non-empty strings")
    elif len(value) != len(set(value)):
        errors.append(f"{label} must not contain duplicates")


def validate_state(data: dict[str, Any]) -> None:
    errors: list[str] = []
    keys = set(data)
    missing = sorted(STATE_KEYS - keys)
    unknown = sorted(keys - STATE_KEYS)
    if missing:
        errors.append(f"missing fields: {', '.join(missing)}")
    if unknown:
        errors.append(f"unknown fields: {', '.join(unknown)}")

    schema_version = data.get("schema_version")
    if isinstance(schema_version, bool) or schema_version != SCHEMA_VERSION:
        errors.append(
            f"unsupported schema_version: {schema_version!r}; supported={SCHEMA_VERSION}"
        )
    for label in ("task_id", "current_step"):
        value = data.get(label)
        if not isinstance(value, str) or not value:
            errors.append(f"{label} must be a non-empty string")
    if not isinstance(data.get("resume_hint"), str):
        errors.append("resume_hint must be a string")

    route = data.get("route")
    if route not in ROUTES:
        errors.append(f"invalid route: {route!r}")
    status = data.get("status")
    if status not in STATUSES:
        errors.append(f"invalid status: {status!r}")
    current_step = data.get("current_step")
    if status == "completed" and current_step != "complete":
        errors.append("completed state must use current_step `complete`")
    if status == "in_progress" and current_step == "complete":
        errors.append("in_progress state must not use current_step `complete`")

    for label in ("completed_steps", "changed_files", "verification"):
        validate_string_list(data.get(label), label, errors)

    created_at = parse_utc_timestamp(data.get("created_at"), "created_at", errors)
    updated_at = parse_utc_timestamp(data.get("updated_at"), "updated_at", errors)
    if created_at is not None and updated_at is not None and updated_at < created_at:
        errors.append("updated_at must not precede created_at")

    if errors:
        raise ValueError("invalid state: " + "; ".join(errors))


def load_state(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"state file does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in state file {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise TypeError("state must be a JSON object")
    validate_state(data)
    return data


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
        "schema_version": SCHEMA_VERSION,
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
        raise ValueError("completed state is immutable; initialize a new state file")
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
    validate_state(state)
    return state


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
    except (TypeError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(state, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
