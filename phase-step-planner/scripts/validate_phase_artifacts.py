#!/usr/bin/env python3
"""Validate phase planning artifacts without modifying the repository."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path


PHASE_STATES = {
    "not-started",
    "in-progress",
    "development-complete",
    "accepted",
    "release-ready",
    "release-blocked",
}
STEP_STATES = {"detailed", "outline", "accepted", "deferred"}
TERMINAL_PHASE_STATES = {"accepted", "release-ready"}
PLACEHOLDER_RE = re.compile(r"\{\{[A-Z][A-Z0-9_]*\}\}")
STATUS_VALUE_RE = re.compile(r"^- (?P<label>[^:]+):\s*(?P<value>.+?)\s*$", re.MULTILINE)
REQUIRED_STATUS_LABELS = {
    "Verified Git checkpoint",
    "Worktree state",
    "Current executable step",
    "Current step specification checkpoint",
    "Audited against repository checkpoint",
    "Phase state",
}
REQUIRED_STEP_HEADINGS = {
    "## One outcome",
    "## Non-goals",
    "## Entry conditions and verified baseline",
    "## File boundary",
    "## Contracts and invariants",
    "## Side-effect policy",
    "## Required pre-code rehearsal",
    "## Acceptance",
    "## Stop and degrade",
    "## Deliverables",
}


def sha256_checkpoint(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def read_utf8(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(f"missing required file: {path}")
    except UnicodeDecodeError as exc:
        errors.append(f"file is not valid UTF-8: {path}: {exc}")
    return ""


def status_values(text: str, errors: list[str]) -> dict[str, str]:
    values: dict[str, str] = {}
    counts: dict[str, int] = {}
    for match in STATUS_VALUE_RE.finditer(text):
        label = match.group("label").strip()
        counts[label] = counts.get(label, 0) + 1
        values[label] = match.group("value").strip()
    for label in sorted(REQUIRED_STATUS_LABELS):
        count = counts.get(label, 0)
        if count == 0:
            errors.append(f"missing required STATUS field: {label}")
        elif count > 1:
            errors.append(f"duplicate required STATUS field: {label}")
    return values


def unquote_code(value: str) -> str:
    if len(value) >= 2 and value.startswith("`") and value.endswith("`"):
        return value[1:-1]
    return value


def parse_step_rows(readme_text: str, errors: list[str]) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for line in readme_text.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 5 or cells[0] in {"Step document", "---"}:
            continue
        if all(set(cell) <= {"-", ":"} for cell in cells):
            continue
        document = unquote_code(cells[0])
        state = cells[4]
        if state not in STEP_STATES:
            errors.append(f"invalid specification state {state!r} for {document!r}")
        rows.append((document, state))
    return rows


def resolve_step(phase_dir: Path, relative: str, errors: list[str]) -> Path | None:
    candidate = Path(relative)
    if candidate.is_absolute() or ".." in candidate.parts:
        errors.append(f"current step must be a safe relative path: {relative!r}")
        return None
    resolved = (phase_dir / candidate).resolve()
    try:
        resolved.relative_to(phase_dir.resolve())
    except ValueError:
        errors.append(f"current step escapes the phase directory: {relative!r}")
        return None
    if not candidate.name.startswith("STEP_") or candidate.suffix.lower() != ".md":
        errors.append(f"current step must match STEP_*.md: {relative!r}")
    return resolved


def validate_phase(phase_dir: Path) -> list[str]:
    errors: list[str] = []
    phase_dir = phase_dir.resolve()
    if not phase_dir.is_dir():
        return [f"phase directory does not exist: {phase_dir}"]

    readme_path = phase_dir / "README.md"
    status_path = phase_dir / "STATUS.md"
    readme_text = read_utf8(readme_path, errors)
    status_text = read_utf8(status_path, errors)

    markdown_files = [path for path in phase_dir.glob("*.md") if path.is_file()]
    for path in markdown_files:
        text = read_utf8(path, errors)
        placeholders = sorted(set(PLACEHOLDER_RE.findall(text)))
        if placeholders:
            errors.append(f"unresolved placeholders in {path.name}: {', '.join(placeholders)}")

    values = status_values(status_text, errors)
    phase_state = values.get("Phase state")
    if phase_state not in PHASE_STATES:
        errors.append(f"invalid or missing Phase state: {phase_state!r}")

    current_raw = values.get("Current executable step")
    checkpoint_raw = values.get("Current step specification checkpoint")
    current = unquote_code(current_raw) if current_raw else None
    checkpoint = unquote_code(checkpoint_raw) if checkpoint_raw else None
    rows = parse_step_rows(readme_text, errors)
    detailed = [document for document, state in rows if state == "detailed"]

    if current == "none":
        if phase_state not in TERMINAL_PHASE_STATES:
            errors.append("Current executable step may be none only for accepted or release-ready phases")
        if checkpoint != "not-applicable":
            errors.append("terminal phase without a current step must use checkpoint `not-applicable`")
        if detailed:
            errors.append("terminal phase without a current step must not contain a detailed step")
        return errors

    if not current:
        errors.append("missing Current executable step")
        return errors
    if len(detailed) != 1:
        errors.append(f"expected exactly one detailed step, found {len(detailed)}")
    elif detailed[0] != current:
        errors.append(
            f"detailed step {detailed[0]!r} does not match Current executable step {current!r}"
        )

    step_path = resolve_step(phase_dir, current, errors)
    if step_path is None or not step_path.is_file():
        if step_path is not None:
            errors.append(f"current step file does not exist: {step_path}")
        return errors

    step_text = read_utf8(step_path, errors)
    missing_headings = sorted(REQUIRED_STEP_HEADINGS - set(step_text.splitlines()))
    if missing_headings:
        errors.append(f"current step is missing required headings: {', '.join(missing_headings)}")

    actual_checkpoint = sha256_checkpoint(step_path)
    if checkpoint != actual_checkpoint:
        errors.append(
            "current step checkpoint mismatch: "
            f"recorded {checkpoint!r}, actual {actual_checkpoint!r}"
        )
    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase_dir", nargs="?", type=Path)
    parser.add_argument("--print-checkpoint", type=Path, metavar="STEP_FILE")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.print_checkpoint:
        if args.phase_dir:
            print("error: phase_dir and --print-checkpoint are mutually exclusive", file=sys.stderr)
            return 2
        if not args.print_checkpoint.is_file():
            print(f"error: step file does not exist: {args.print_checkpoint}", file=sys.stderr)
            return 2
        print(sha256_checkpoint(args.print_checkpoint))
        return 0
    if not args.phase_dir:
        print("error: phase_dir is required", file=sys.stderr)
        return 2

    errors = validate_phase(args.phase_dir)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAIL: {len(errors)} validation error(s)")
        return 1
    print("PASS: phase artifacts are internally consistent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
