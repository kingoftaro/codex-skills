#!/usr/bin/env python3
"""Check handoff structure and fixtures; prose hints are advisory only."""

from __future__ import annotations

import re
import tempfile
from pathlib import Path

from validate_phase_artifacts import (
    REQUIRED_STEP_HEADINGS,
    STEP_HANDOFF_SCHEMA_RE,
    SUPPORTED_HANDOFF_SCHEMA,
    sha256_checkpoint,
    status_values,
    unquote_code,
    validate_phase,
)

STEP_BODY = """# STEP_001: Freeze contract

## One outcome
Freeze one interface.

## Non-goals
- Adapter work

## Entry conditions and verified baseline
- Handoff schema: 1
- Review route: Fast
- Baseline is green

## File boundary
| Access | Path | Purpose |
|---|---|---|
| Modify | `src/contract.py` | Freeze interface |

## Contracts and invariants
- Stable return type

## Side-effect policy
- No external effects

## Required pre-code rehearsal
Report exact touchpoints and stop conditions.

## Acceptance
- Contract test passes

## Stop and degrade
- Stop on an incompatible caller

## Deliverables
- Contract and tests
"""


def contains_phrase(text: str, phrase: str) -> bool:
    """Match a declaration without making Markdown line wrapping significant."""

    return " ".join(phrase.split()) in " ".join(text.split())


def make_phase(root: Path) -> tuple[Path, Path]:
    step = root / "STEP_001_freeze_contract.md"
    step.write_text(STEP_BODY, encoding="utf-8")
    root.joinpath("README.md").write_text(
        "# Phase P1 implementation index\n\n"
        "| Step document | One outcome | Depends on | Primary risk boundary | Specification state |\n"
        "|---|---|---|---|---|\n"
        "| `STEP_001_freeze_contract.md` | Freeze contract | none | compatibility | detailed |\n",
        encoding="utf-8",
    )
    status = root / "STATUS.md"
    status.write_text(
        "# Phase P1 current status\n\n"
        "- Handoff schema: 1\n"
        "- Review result: PASS\n"
        '- Repair loop: `{"state":"inactive","invariant_id":"none",'
        '"consecutive_regressions":0,"last_classification":"none",'
        '"evidence":"none"}`\n'
        "- Verified Git checkpoint: `abc123`\n"
        "- Worktree state: clean\n"
        "- Phase state: in-progress\n"
        "- Current executable step: `STEP_001_freeze_contract.md`\n"
        f"- Current step specification checkpoint: `{sha256_checkpoint(step)}`\n"
        "- Audited against repository checkpoint: `abc123`\n",
        encoding="utf-8",
    )
    return status, step


def validate_declarations(repository_root: Path) -> tuple[list[str], list[str]]:
    """Check files, discoverable references, and the bundled template schema."""
    failures: list[str] = []
    warnings: list[str] = []
    skill_root = repository_root / "phase-step-planner"
    executor_skill = repository_root / "deliver-code-change" / "SKILL.md"
    planner_agent = skill_root / "agents" / "openai.yaml"
    executor_agent = repository_root / "deliver-code-change" / "agents" / "openai.yaml"
    executor_routing = (
        repository_root / "deliver-code-change" / "references" / "routing.md"
    )
    planner_failures = skill_root / "references" / "FAILURE_PATTERNS.md"
    planner_repair_loop = skill_root / "references" / "repair-loop.md"
    planner_step_template = skill_root / "assets" / "STEP_TEMPLATE.md"
    planner_status_template = skill_root / "assets" / "STATUS_TEMPLATE.md"
    planner_readme_template = skill_root / "assets" / "PHASE_README_TEMPLATE.md"
    executor_handoff = (
        repository_root / "deliver-code-change" / "references" / "phase-handoff.md"
    )

    required_files = (
        skill_root / "SKILL.md",
        executor_skill,
        planner_agent,
        executor_agent,
        executor_routing,
        planner_failures,
        planner_repair_loop,
        planner_step_template,
        planner_status_template,
        planner_readme_template,
        executor_handoff,
    )
    for path in required_files:
        if not path.is_file():
            failures.append(f"missing required resource: {path.relative_to(repository_root)}")
    if failures:
        return failures, warnings

    for entrypoint, required_reference in (
        (executor_skill, executor_handoff),
        (skill_root / "SKILL.md", planner_repair_loop),
    ):
        targets: set[Path] = set()
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", entrypoint.read_text(encoding="utf-8")):
            clean = target.split("#", 1)[0]
            if not clean or re.match(r"^[a-z]+://", clean, re.IGNORECASE):
                continue
            resolved = (entrypoint.parent / clean).resolve()
            targets.add(resolved)
            if not resolved.is_file():
                failures.append(f"broken reference in {entrypoint.name}: {target}")
        if required_reference.resolve() not in targets:
            failures.append(f"{entrypoint} must link to {required_reference.name}")

    status_text = planner_status_template.read_text(encoding="utf-8")
    step_text = planner_step_template.read_text(encoding="utf-8")
    step_lines = step_text.splitlines()
    values = status_values(status_text, failures)
    if unquote_code(values.get("Handoff schema", "")) != SUPPORTED_HANDOFF_SCHEMA:
        failures.append("STATUS template must declare the supported handoff schema")
    schemas = STEP_HANDOFF_SCHEMA_RE.findall(step_text)
    if len(schemas) != 1 or unquote_code(schemas[0].strip()) != SUPPORTED_HANDOFF_SCHEMA:
        failures.append("STEP template must declare one supported handoff schema")
    for heading in sorted(REQUIRED_STEP_HEADINGS):
        if step_lines.count(heading) != 1:
            failures.append(f"STEP template must contain one {heading!r} section")
    index_lines = planner_readme_template.read_text(encoding="utf-8").splitlines()
    if not any(
        len(cells := [cell.strip() for cell in line.strip().strip("|").split("|")]) == 5
        and cells[0] == "Step document"
        for line in index_lines if line.lstrip().startswith("|")
    ):
        failures.append("phase index template must contain a five-column step table")

    # Cheap reminders for maintainers, not semantic correctness or execution gates.
    for path, phrase in (
        (skill_root / "SKILL.md", "Do not review every draft"),
        (skill_root / "SKILL.md", "one initial review and one focused delta review"),
        (executor_routing, "Keep ordinary exploration, review, and trivial edits direct"),
        (executor_handoff, "executor never refreshes the hash"),
    ):
        if not contains_phrase(path.read_text(encoding="utf-8"), phrase):
            warnings.append(
                f"{path.relative_to(repository_root)}: prose hint {phrase!r} changed; "
                "review its meaning if needed (equivalent wording is allowed)"
            )
    return failures, warnings


def validate_fixtures() -> list[str]:
    failures: list[str] = []

    with tempfile.TemporaryDirectory() as temporary:
        phase = Path(temporary)
        status, step = make_phase(phase)
        valid_errors = validate_phase(phase)
        if valid_errors:
            failures.append(f"valid handoff failed validation: {valid_errors}")

        original_status = status.read_text(encoding="utf-8")
        status.write_text(
            original_status.replace("- Review result: PASS", "- Review result: STALE"),
            encoding="utf-8",
        )
        stale_errors = validate_phase(phase)
        if not any("not executable" in error for error in stale_errors):
            failures.append("STALE handoff was not rejected")

        status.write_text(original_status, encoding="utf-8")
        step.write_text(STEP_BODY + "\nChanged after preparation.\n", encoding="utf-8")
        drift_errors = validate_phase(phase)
        if not any("checkpoint mismatch" in error for error in drift_errors):
            failures.append("STEP checkpoint drift was not rejected")

        step.write_text(STEP_BODY, encoding="utf-8")
        status.write_text(
            original_status.replace("- Handoff schema: 1", "- Handoff schema: 99"),
            encoding="utf-8",
        )
        if not any("unsupported" in error for error in validate_phase(phase)):
            failures.append("unsupported handoff schema was not rejected")
    return failures


def main() -> int:
    repository_root = Path(__file__).resolve().parents[2]
    failures, warnings = validate_declarations(repository_root)
    failures.extend(validate_fixtures())
    for warning in warnings:
        print(f"WARNING: {warning}")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        print(f"Validation failed with {len(failures)} issue(s).")
        return 1

    print(
        "PASS: handoff resources, template structure, and adversarial fixtures "
        "are consistent; prose hints are advisory and semantics need review"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
