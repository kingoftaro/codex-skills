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
PHASE_STATE_PATTERN = re.compile(r"^- Phase state:\s*(.+?)\s*$", re.MULTILINE)
STEP_REVIEW_RESULT_PATTERN = re.compile(
    r"^- Pre-step consistency review:\s*(PASS|STALE|BLOCKED)\s*$", re.MULTILINE
)
STATUS_REVIEW_CHECKPOINT_PATTERN = re.compile(
    r"^- Repository/worktree checkpoint reviewed:\s*(.+?)\s*$", re.MULTILINE
)
STEP_REVIEW_CHECKPOINT_PATTERN = re.compile(
    r"^- Reviewed repository/worktree checkpoint:\s*(.+?)\s*$", re.MULTILINE
)
SUPPORTED_SCHEMA = "1"
SUPPORTED_PHASE_STATES = {
    "not started",
    "in progress",
    "development complete",
    "accepted",
    "release blocked",
}
NON_EXECUTABLE_PHASE_STATES = {"development complete", "accepted"}
PLACEHOLDER_PATTERN = re.compile(r"\{\{[A-Z][A-Z0-9_]*\}\}")
TEMPLATE_NAMES = ("STATUS_TEMPLATE.md", "STEP_TEMPLATE.md")
REQUIRED_STEP_SECTIONS = (
    "Handoff contract",
    "One outcome",
    "Non-goals",
    "Entry conditions and verified baseline",
    "File boundary",
    "Contracts and invariants",
    "Side-effect policy",
    "Implementation order",
    "Required pre-code rehearsal",
    "Acceptance",
    "Stop and degrade",
    "Deliverables",
)
REQUIRED_ACCEPTANCE_SECTIONS = (
    "Normal cases",
    "Failure and adversarial cases",
    "Validation commands",
)


def sha256(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def single_match(pattern: re.Pattern[str], text: str, label: str) -> str:
    matches = pattern.findall(text)
    if len(matches) != 1:
        raise ValueError(f"STATUS.md must contain exactly one valid {label}; found {len(matches)}")
    return matches[0]


def bundled_template_placeholders() -> set[str]:
    assets = Path(__file__).resolve().parent.parent / "assets"
    placeholders: set[str] = set()
    for name in TEMPLATE_NAMES:
        template = assets / name
        if not template.is_file():
            raise ValueError(f"bundled handoff template is missing: {template}")
        placeholders.update(PLACEHOLDER_PATTERN.findall(template.read_text(encoding="utf-8")))
    return placeholders


def reject_unresolved_placeholders(text: str, label: str) -> None:
    unresolved = sorted(set(PLACEHOLDER_PATTERN.findall(text)) & bundled_template_placeholders())
    if unresolved:
        raise ValueError(
            f"{label} contains unresolved bundled template placeholders: "
            + ", ".join(unresolved)
        )


def section_body(text: str, level: int, title: str) -> str:
    marker = "#" * level
    pattern = re.compile(
        rf"^{re.escape(marker)}\s+{re.escape(title)}\s*$"
        rf"(?P<body>.*?)(?=^{'#' * level}\s+|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    matches = list(pattern.finditer(text))
    if len(matches) != 1:
        raise ValueError(
            f"current STEP must contain exactly one {marker} {title} section; "
            f"found {len(matches)}"
        )
    body = matches[0].group("body").strip()
    substantive_lines = [
        line.strip()
        for line in body.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not substantive_lines:
        raise ValueError(f"current STEP section {marker} {title} has no content")
    return body


def validate_step_structure(text: str) -> None:
    for title in REQUIRED_STEP_SECTIONS:
        section_body(text, 2, title)
    acceptance = section_body(text, 2, "Acceptance")
    for title in REQUIRED_ACCEPTANCE_SECTIONS:
        section_body(acceptance, 3, title)


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
    reject_unresolved_placeholders(text, "STATUS.md")
    phase_state = single_match(PHASE_STATE_PATTERN, text, "Phase state")
    if phase_state not in SUPPORTED_PHASE_STATES:
        raise ValueError(f"unsupported phase state: {phase_state}")
    if phase_state in NON_EXECUTABLE_PHASE_STATES:
        raise ValueError(f"phase state is not executable: {phase_state}")
    relative = single_match(STEP_PATTERN, text, "Current executable step")
    expected = single_match(CHECKPOINT_PATTERN, text, "Current STEP checkpoint")
    step = resolve_inside(root, relative)
    step_text = step.read_text(encoding="utf-8")
    reject_unresolved_placeholders(step_text, "current STEP")
    validate_step_structure(step_text)

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

    step_review = single_match(
        STEP_REVIEW_RESULT_PATTERN,
        step_text,
        "pre-step consistency review in STEP",
    )
    if step_review != "PASS":
        raise ValueError(f"STEP pre-step consistency review is not executable: {step_review}")

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
            print(f"PASS: {step} has a complete handoff structure and matches {checkpoint}")
    except (OSError, UnicodeError, ValueError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
