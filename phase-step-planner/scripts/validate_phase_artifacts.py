#!/usr/bin/env python3
"""Compute a STEP digest or validate a versioned phase handoff."""

from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path


STEP_PATTERN = re.compile(r"^- Current executable step:\s*`([^`]+)`\s*$", re.MULTILINE)
CHECKPOINT_PATTERN = re.compile(
    r"^- Current STEP checkpoint:\s*`(sha256:[0-9a-f]{64})`\s*$", re.MULTILINE
)
SCHEMA_PATTERN = re.compile(r"^- Handoff schema version:\s*([^\s]+)\s*$", re.MULTILINE)
STATUS_BASELINE_PATTERN = re.compile(
    r"^- Schema/migration version:\s*(.+?)\s*$", re.MULTILINE
)
STEP_BASELINE_PATTERN = re.compile(
    r"^- Current schema/migration:\s*(.+?)\s*$", re.MULTILINE
)
REVIEW_RESULT_PATTERN = re.compile(r"^- Result:\s*(PASS|STALE|BLOCKED)\s*$", re.MULTILINE)
STATUS_REVIEW_CHECKPOINT_PATTERN = re.compile(
    r"^- Repository/worktree checkpoint reviewed:\s*(.+?)\s*$", re.MULTILINE
)
STEP_REVIEW_CHECKPOINT_PATTERN = re.compile(
    r"^- Reviewed repository/worktree checkpoint:\s*(.+?)\s*$", re.MULTILINE
)
SUPPORTED_SCHEMA = "1"


def sha256(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def single_match(pattern: re.Pattern[str], text: str, label: str) -> str:
    matches = pattern.findall(text)
    if len(matches) != 1:
        raise ValueError(f"STATUS.md must contain exactly one valid {label}; found {len(matches)}")
    return matches[0]


def resolve_inside(root: Path, relative: str) -> Path:
    candidate = Path(relative)
    if candidate.is_absolute():
        raise ValueError("current STEP path must be relative to the phase directory")
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError("current STEP path escapes the phase directory") from exc
    if not resolved.is_file():
        raise ValueError(f"current STEP does not exist or is not a file: {relative}")
    return resolved


def validate(phase_dir: Path) -> tuple[Path, str]:
    root = phase_dir.resolve()
    status = root / "STATUS.md"
    if not status.is_file():
        raise ValueError(f"STATUS.md is missing: {status}")
    text = status.read_text(encoding="utf-8")
    relative = single_match(STEP_PATTERN, text, "Current executable step")
    expected = single_match(CHECKPOINT_PATTERN, text, "Current STEP checkpoint")
    step = resolve_inside(root, relative)
    step_text = step.read_text(encoding="utf-8")

    status_schema = single_match(SCHEMA_PATTERN, text, "Handoff schema version")
    step_schema = single_match(SCHEMA_PATTERN, step_text, "Handoff schema version in STEP")
    if status_schema != SUPPORTED_SCHEMA or step_schema != SUPPORTED_SCHEMA:
        raise ValueError(
            f"unsupported or mixed handoff schema: STATUS={status_schema}, "
            f"STEP={step_schema}, supported={SUPPORTED_SCHEMA}"
        )

    result = single_match(REVIEW_RESULT_PATTERN, text, "pre-step consistency Result")
    if result != "PASS":
        raise ValueError(f"pre-step consistency Result is not executable: {result}")

    status_baseline = single_match(
        STATUS_BASELINE_PATTERN, text, "Schema/migration version"
    )
    step_baseline = single_match(
        STEP_BASELINE_PATTERN, step_text, "Current schema/migration"
    )
    if status_baseline != step_baseline:
        raise ValueError(
            "schema/migration baseline mismatch: "
            f"STATUS={status_baseline!r}, STEP={step_baseline!r}"
        )

    status_review = single_match(
        STATUS_REVIEW_CHECKPOINT_PATTERN,
        text,
        "Repository/worktree checkpoint reviewed",
    )
    step_review = single_match(
        STEP_REVIEW_CHECKPOINT_PATTERN,
        step_text,
        "Reviewed repository/worktree checkpoint",
    )
    if status_review != step_review:
        raise ValueError(
            "reviewed repository/worktree checkpoint mismatch: "
            f"STATUS={status_review!r}, STEP={step_review!r}"
        )

    actual = sha256(step)
    if actual != expected:
        raise ValueError(f"current STEP checkpoint mismatch: expected {expected}, actual {actual}")
    return step, actual


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("phase_dir", nargs="?", help="phase directory containing STATUS.md")
    mode.add_argument("--digest", metavar="STEP_PATH", help="print the SHA-256 checkpoint for one STEP")
    args = parser.parse_args()
    try:
        if args.digest:
            step = Path(args.digest).resolve()
            if not step.is_file():
                raise ValueError(f"STEP does not exist or is not a file: {step}")
            print(sha256(step))
        else:
            step, checkpoint = validate(Path(args.phase_dir))
            print(f"PASS: {step} matches {checkpoint}")
    except (OSError, UnicodeError, ValueError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
