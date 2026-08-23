#!/usr/bin/env python3
"""Validate the bundled planner-to-executor handoff contract."""

from __future__ import annotations

import tempfile
from pathlib import Path

from validate_phase_artifacts import sha256_checkpoint, validate_phase

STEP_BODY = """# STEP_001: Freeze contract

## One outcome
Freeze one interface.

## Non-goals
- Adapter work

## Entry conditions and verified baseline
- Handoff schema: 1
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


def main() -> int:
    failures: list[str] = []
    skill_root = Path(__file__).resolve().parent.parent
    repository_root = skill_root.parent
    executor_skill = repository_root / "deliver-code-change" / "SKILL.md"
    planner_agent = skill_root / "agents" / "openai.yaml"
    executor_agent = repository_root / "deliver-code-change" / "agents" / "openai.yaml"
    executor_routing = (
        repository_root / "deliver-code-change" / "references" / "routing.md"
    )
    planner_failures = skill_root / "references" / "FAILURE_PATTERNS.md"
    planner_repair_loop = skill_root / "references" / "repair-loop.md"
    executor_handoff = (
        repository_root / "deliver-code-change" / "references" / "phase-handoff.md"
    )

    required_files = (
        executor_skill,
        planner_agent,
        executor_agent,
        executor_routing,
        planner_failures,
        planner_repair_loop,
        executor_handoff,
    )
    if not all(path.is_file() for path in required_files):
        failures.append(
            "adjacent skills, agent metadata, routing, repair-loop, and handoff "
            "references are required"
        )
    else:
        planner_text = skill_root.joinpath("SKILL.md").read_text(encoding="utf-8")
        skill_text = executor_skill.read_text(encoding="utf-8")
        planner_agent_text = planner_agent.read_text(encoding="utf-8")
        executor_agent_text = executor_agent.read_text(encoding="utf-8")
        routing_text = executor_routing.read_text(encoding="utf-8")
        failure_text = planner_failures.read_text(encoding="utf-8")
        repair_loop_text = planner_repair_loop.read_text(encoding="utf-8")
        handoff_text = executor_handoff.read_text(encoding="utf-8")
        for phrase, text, label in (
            ("Do not use for trivial", skill_text, "executor frontmatter"),
            ("do not use to plan a multi-stage phase", skill_text, "executor frontmatter"),
            ("Do not use for one bounded change", planner_text, "planner frontmatter"),
            ("should not be invoked for a trivial edit", routing_text, "direct-edit routing"),
            ("non-trivial bounded code change", executor_agent_text, "executor agent metadata"),
            ("multi-stage phase", planner_agent_text, "planner agent metadata"),
            ("Repair-loop Circuit Breaker", planner_text, "planner repair-loop gate"),
            (
                "Symptom patch creates an adjacent regression",
                failure_text,
                "planner repair-loop pattern",
            ),
            ("repair-loop circuit breaker", handoff_text, "executor repair-loop return"),
        ):
            if phrase not in text:
                failures.append(f"{label} is missing routing contract phrase {phrase!r}")
        if "[references/phase-handoff.md](references/phase-handoff.md)" not in skill_text:
            failures.append("executor SKILL.md does not route phase-managed work to phase-handoff.md")
        if "[references/repair-loop.md](references/repair-loop.md)" not in planner_text:
            failures.append("planner SKILL.md does not route active repair loops to repair-loop.md")
        for term in (
            "consecutive_regressions",
            "independent acceptance or rollback boundaries",
            "root-cause evidence",
        ):
            if term not in repair_loop_text:
                failures.append(f"planner repair-loop contract is missing {term!r}")
        for phrase in (
            "authoritative validator",
            "Review result",
            "Handoff schema",
            "current executable STEP",
            "sha256:",
        ):
            if phrase not in handoff_text:
                failures.append(f"executor handoff contract is missing {phrase!r}")

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

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        print(f"Validation failed with {len(failures)} issue(s).")
        return 1

    print(
        "PASS: bundled routing and handoff declarations plus adversarial phase "
        "fixtures are consistent"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
