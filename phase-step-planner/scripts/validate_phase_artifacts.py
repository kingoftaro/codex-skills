#!/usr/bin/env python3
"""Validate phase planning artifacts without modifying the repository."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
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
SUPPORTED_HANDOFF_SCHEMA = "1"
REVIEW_RESULTS = {"PASS", "STALE", "BLOCKED", "NOT_APPLICABLE"}
REPAIR_LOOP_STATES = {"inactive", "observing", "blocked", "reset"}
REPAIR_CLASSIFICATIONS = {
    "none",
    "latent",
    "repair-introduced",
    "environment-evidence",
}
REPAIR_LOOP_KEYS = {
    "state",
    "invariant_id",
    "consecutive_regressions",
    "last_classification",
    "evidence",
}
PLACEHOLDER_RE = re.compile(r"\{\{[A-Z][A-Z0-9_]*\}\}")
STATUS_VALUE_RE = re.compile(r"^- (?P<label>[^:]+):\s*(?P<value>.+?)\s*$", re.MULTILINE)
STEP_HANDOFF_SCHEMA_RE = re.compile(
    r"^- Handoff schema:\s*(?P<value>.+?)\s*$", re.MULTILINE
)
REQUIRED_STATUS_LABELS = {
    "Handoff schema",
    "Review result",
    "Repair loop",
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


@dataclass
class PhaseValidation:
    errors: list[str] = field(default_factory=list)
    pending: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)

    @property
    def issues(self) -> list[str]:
        return self.errors + self.conflicts + self.pending

    @property
    def outcome(self) -> str:
        if self.errors:
            return "FAIL"
        if self.conflicts:
            return "BLOCKED"
        if self.pending:
            return "STALE"
        return "PASS"


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


def repair_loop_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    values: dict[str, object] = {}
    for key, value in pairs:
        if key in values:
            raise ValueError(f"duplicate key {key!r}")
        values[key] = value
    return values


def parse_repair_loop(
    raw_value: str | None,
    review_result: str | None,
    errors: list[str],
) -> str | None:
    if raw_value is None:
        return None
    value = unquote_code(raw_value)
    try:
        repair = json.loads(value, object_pairs_hook=repair_loop_object)
    except json.JSONDecodeError as exc:
        errors.append(f"invalid Repair loop JSON: {exc.msg}")
        return None
    except ValueError as exc:
        errors.append(f"invalid Repair loop JSON: {exc}")
        return None
    if not isinstance(repair, dict):
        errors.append("Repair loop must be a JSON object")
        return None

    keys = set(repair)
    missing = sorted(REPAIR_LOOP_KEYS - keys)
    unknown = sorted(keys - REPAIR_LOOP_KEYS)
    if missing:
        errors.append(f"Repair loop is missing fields: {', '.join(missing)}")
    if unknown:
        errors.append(f"Repair loop contains unknown fields: {', '.join(unknown)}")
    if missing or unknown:
        return None

    state = repair["state"]
    invariant_id = repair["invariant_id"]
    regressions = repair["consecutive_regressions"]
    classification = repair["last_classification"]
    evidence = repair["evidence"]

    if not isinstance(state, str) or state not in REPAIR_LOOP_STATES:
        errors.append(f"invalid Repair loop state: {state!r}")
        state = None
    for label, item in (("invariant_id", invariant_id), ("evidence", evidence)):
        if not isinstance(item, str) or not item.strip():
            errors.append(f"Repair loop {label} must be a non-empty string")
    if not isinstance(classification, str) or classification not in REPAIR_CLASSIFICATIONS:
        errors.append(f"invalid Repair loop last_classification: {classification!r}")
    if isinstance(regressions, bool) or not isinstance(regressions, int) or regressions < 0:
        errors.append("Repair loop consecutive_regressions must be a non-negative integer")
        return state
    if state is None or not isinstance(invariant_id, str) or not isinstance(evidence, str):
        return state

    if state == "inactive":
        if (invariant_id, regressions, classification, evidence) != (
            "none",
            0,
            "none",
            "none",
        ):
            errors.append(
                "inactive Repair loop must use invariant_id/evidence/classification `none` "
                "and zero consecutive_regressions"
            )
    elif state == "observing":
        if regressions != 1:
            errors.append("observing Repair loop must have exactly one consecutive regression")
        if invariant_id == "none" or evidence == "none":
            errors.append("observing Repair loop requires invariant_id and evidence")
        if classification != "repair-introduced":
            errors.append(
                "observing Repair loop last_classification must be `repair-introduced`"
            )
    elif state == "blocked":
        if regressions < 2:
            errors.append("blocked Repair loop requires at least two consecutive regressions")
        if invariant_id == "none" or evidence == "none":
            errors.append("blocked Repair loop requires invariant_id and evidence")
        if classification != "repair-introduced":
            errors.append(
                "blocked Repair loop last_classification must be `repair-introduced`"
            )
        if review_result != "BLOCKED":
            errors.append("blocked Repair loop requires Review result `BLOCKED`")
    elif state == "reset":
        if regressions != 0:
            errors.append("reset Repair loop must have zero consecutive regressions")
        if invariant_id == "none" or evidence == "none":
            errors.append("reset Repair loop requires invariant_id and root-cause evidence")
        if classification != "repair-introduced":
            errors.append("reset Repair loop last_classification must be `repair-introduced`")
    return state


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


def inspect_phase(phase_dir: Path) -> PhaseValidation:
    result = PhaseValidation()
    errors = result.errors
    phase_dir = phase_dir.resolve()
    if not phase_dir.is_dir():
        errors.append(f"phase directory does not exist: {phase_dir}")
        return result

    readme_path = phase_dir / "README.md"
    status_path = phase_dir / "STATUS.md"
    readme_text = read_utf8(readme_path, errors)
    status_text = read_utf8(status_path, errors)

    # Only authoritative handoff materials can block current execution.
    for path, text in ((readme_path, readme_text), (status_path, status_text)):
        placeholders = sorted(set(PLACEHOLDER_RE.findall(text)))
        if placeholders:
            errors.append(f"unresolved placeholders in {path.name}: {', '.join(placeholders)}")

    values = status_values(status_text, errors)
    phase_state = values.get("Phase state")
    if phase_state not in PHASE_STATES:
        errors.append(f"invalid or missing Phase state: {phase_state!r}")

    handoff_schema_raw = values.get("Handoff schema")
    handoff_schema = unquote_code(handoff_schema_raw) if handoff_schema_raw else None
    if handoff_schema != SUPPORTED_HANDOFF_SCHEMA:
        errors.append(
            "unsupported or missing Handoff schema: "
            f"{handoff_schema!r}; supported={SUPPORTED_HANDOFF_SCHEMA!r}"
        )

    review_result_raw = values.get("Review result")
    review_result = unquote_code(review_result_raw) if review_result_raw else None
    if review_result not in REVIEW_RESULTS:
        errors.append(f"invalid or missing Review result: {review_result!r}")
    repair_state = parse_repair_loop(values.get("Repair loop"), review_result, errors)

    verified_checkpoint_raw = values.get("Verified Git checkpoint")
    audited_checkpoint_raw = values.get("Audited against repository checkpoint")
    verified_checkpoint = (
        unquote_code(verified_checkpoint_raw) if verified_checkpoint_raw else None
    )
    audited_checkpoint = (
        unquote_code(audited_checkpoint_raw) if audited_checkpoint_raw else None
    )
    if (
        verified_checkpoint
        and audited_checkpoint
        and verified_checkpoint != audited_checkpoint
    ):
        result.conflicts.append(
            "Verified Git checkpoint and audited repository checkpoint do not match: "
            f"verified={verified_checkpoint!r}, audited={audited_checkpoint!r}"
        )

    current_raw = values.get("Current executable step")
    checkpoint_raw = values.get("Current step specification checkpoint")
    current = unquote_code(current_raw) if current_raw else None
    checkpoint = unquote_code(checkpoint_raw) if checkpoint_raw else None
    rows = parse_step_rows(readme_text, errors)
    detailed = [document for document, state in rows if state == "detailed"]

    if current == "none":
        if phase_state not in TERMINAL_PHASE_STATES:
            errors.append("Current executable step may be none only for accepted or release-ready phases")
        if review_result != "NOT_APPLICABLE":
            errors.append("terminal phase without a current step must use Review result `NOT_APPLICABLE`")
        if checkpoint != "not-applicable":
            errors.append("terminal phase without a current step must use checkpoint `not-applicable`")
        if detailed:
            errors.append("terminal phase without a current step must not contain a detailed step")
        if repair_state != "inactive":
            errors.append("terminal phase without a current step must use inactive Repair loop")
        return result

    if not current:
        errors.append("missing Current executable step")
        return result
    if phase_state in TERMINAL_PHASE_STATES:
        errors.append("terminal phase must not identify a current executable step")
    if review_result != "PASS":
        target = (
            result.pending if review_result == "STALE"
            else result.conflicts if review_result == "BLOCKED"
            else errors
        )
        target.append(
            f"current handoff is not executable: Review result must be `PASS`, got {review_result!r}"
        )
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
        return result

    step_text = read_utf8(step_path, errors)
    placeholders = sorted(set(PLACEHOLDER_RE.findall(step_text)))
    if placeholders:
        errors.append(
            f"unresolved placeholders in current step {step_path.name}: {', '.join(placeholders)}"
        )
    step_lines = step_text.splitlines()
    heading_counts = {heading: step_lines.count(heading) for heading in REQUIRED_STEP_HEADINGS}
    missing_headings = sorted(heading for heading, count in heading_counts.items() if count == 0)
    if missing_headings:
        errors.append(f"current step is missing required headings: {', '.join(missing_headings)}")
    duplicate_headings = sorted(
        heading for heading, count in heading_counts.items() if count > 1
    )
    if duplicate_headings:
        errors.append(
            f"current step contains duplicate required headings: {', '.join(duplicate_headings)}"
        )
    empty_headings: list[str] = []
    for heading, count in heading_counts.items():
        if count != 1:
            continue
        start = step_lines.index(heading) + 1
        end = next(
            (
                index
                for index in range(start, len(step_lines))
                if step_lines[index].startswith("## ")
            ),
            len(step_lines),
        )
        if not any(line.strip() for line in step_lines[start:end]):
            empty_headings.append(heading)
    if empty_headings:
        errors.append(
            f"current step contains empty required sections: {', '.join(sorted(empty_headings))}"
        )

    step_schema_matches = STEP_HANDOFF_SCHEMA_RE.findall(step_text)
    if len(step_schema_matches) != 1:
        errors.append(
            "current step must declare exactly one `- Handoff schema:` field, "
            f"found {len(step_schema_matches)}"
        )
    else:
        step_schema = unquote_code(step_schema_matches[0].strip())
        if step_schema != handoff_schema:
            errors.append(
                "STATUS and STEP handoff schemas do not match: "
                f"STATUS={handoff_schema!r}, STEP={step_schema!r}"
            )

    actual_checkpoint = sha256_checkpoint(step_path)
    if checkpoint != actual_checkpoint:
        result.pending.append(
            "current step checkpoint mismatch: "
            f"recorded {checkpoint!r}, actual {actual_checkpoint!r}; "
            "classify attributable post-readiness drift as STALE, then use "
            "route-level review for material deltas or focused confirmation "
            "for clearly non-material deltas; unexplained or materially "
            "conflicting drift is BLOCKED"
        )
    return result


def validate_phase(phase_dir: Path) -> list[str]:
    """Preserve the list-of-issues API used by existing callers."""
    return inspect_phase(phase_dir).issues


def document_warnings(phase_dir: Path) -> list[str]:
    """Optional directory hygiene; never establishes handoff readiness."""
    warnings: list[str] = []
    for path in sorted(phase_dir.glob("*.md")):
        if not path.is_file():
            continue
        try:
            text = read_utf8(path, warnings)
        except OSError as exc:
            warnings.append(f"could not read optional document {path.name}: {exc}")
            continue
        placeholders = sorted(set(PLACEHOLDER_RE.findall(text)))
        if placeholders:
            warnings.append(f"unresolved placeholders in {path.name}: {', '.join(placeholders)}")
    return warnings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase_dir", nargs="?", type=Path)
    parser.add_argument("--print-checkpoint", type=Path, metavar="STEP_FILE")
    parser.add_argument(
        "--check-all-docs", action="store_true",
        help="also report directory-wide document hygiene warnings (non-blocking)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.print_checkpoint:
        if args.phase_dir or args.check_all_docs:
            print("error: --print-checkpoint cannot be combined with phase validation", file=sys.stderr)
            return 2
        if not args.print_checkpoint.is_file():
            print(f"error: step file does not exist: {args.print_checkpoint}", file=sys.stderr)
            return 2
        print(sha256_checkpoint(args.print_checkpoint))
        return 0
    if not args.phase_dir:
        print("error: phase_dir is required", file=sys.stderr)
        return 2

    result = inspect_phase(args.phase_dir)
    if args.check_all_docs:
        for warning in document_warnings(args.phase_dir):
            print(f"WARNING: {warning}")
    if result.issues:
        for error in result.errors:
            print(f"ERROR: {error}")
        for conflict in result.conflicts:
            print(f"CONFLICT: {conflict}")
        for pending in result.pending:
            print(f"PENDING: {pending}")
        print(f"{result.outcome}: handoff is not executable; {len(result.issues)} issue(s)")
        if result.pending:
            print("Pending review or STEP drift needs planner classification; the validator does not determine its origin or update STATUS.")
        return 1
    print(
        "PASS: phase artifacts are structurally and internally consistent; "
        "semantic and live-repository review remain separate"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
