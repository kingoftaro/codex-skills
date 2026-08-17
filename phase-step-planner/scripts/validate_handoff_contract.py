#!/usr/bin/env python3
"""Validate the planner/executor handoff contract and adversarial cases."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path
from typing import Callable


sys.dont_write_bytecode = True
PLANNER = Path(__file__).resolve().parent.parent
WORKSPACE = PLANNER.parent
EXECUTOR_HANDOFF = WORKSPACE / "deliver-code-change" / "references" / "phase-handoff.md"
VALIDATOR = PLANNER / "scripts" / "validate_phase_artifacts.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("phase_handoff_validator", VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load validator: {VALIDATOR}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def require(text: str, fragments: tuple[str, ...], source: Path) -> None:
    missing = [fragment for fragment in fragments if fragment not in text]
    if missing:
        raise AssertionError(f"{source} is missing contract fragments: {missing}")


def expect_rejected(action: Callable[[], object], message: str) -> None:
    try:
        action()
    except ValueError as exc:
        if message not in str(exc):
            raise AssertionError(f"expected {message!r}, got {exc!r}") from exc
    else:
        raise AssertionError(f"expected rejection containing {message!r}")


def step_text(
    schema: str = "1",
    baseline: str = "schema-7",
    checkpoint: str = "git:abc",
    review: str = "PASS",
) -> str:
    return (
        "# STEP_01: example\n\n"
        "## Handoff contract\n\n"
        f"- Handoff schema version: {schema}\n"
        f"- Current schema/migration: {baseline}\n"
        f"- Reviewed repository/worktree checkpoint: {checkpoint}\n"
        f"- Pre-step consistency review: {review}\n"
        "\n## One outcome\n\n- Deliver one verified example.\n"
        "\n## Non-goals\n\n- Do not change unrelated behavior.\n"
        "\n## Entry conditions and verified baseline\n\n- Baseline evidence is current.\n"
        "\n## File boundary\n\n- Modify only `example.py`.\n"
        "\n## Contracts and invariants\n\n- Preserve the example contract.\n"
        "\n## Side-effect policy\n\n- No external effects are allowed.\n"
        "\n## Implementation order\n\n1. Implement.\n2. Verify.\n"
        "\n## Required pre-code rehearsal\n\n- Trace the call path.\n"
        "\n## Acceptance\n\n"
        "### Normal cases\n\n- The example succeeds.\n"
        "\n### Failure and adversarial cases\n\n- Invalid input is rejected.\n"
        "\n### Validation commands\n\n- Run `python -m unittest`.\n"
        "\n## Stop and degrade\n\n- Stop when scope is insufficient.\n"
        "\n## Deliverables\n\n- Code and evidence.\n"
    )


def status_text(
    checkpoint: str,
    *,
    schema: str = "1",
    result: str = "PASS",
    phase_state: str = "in progress",
    baseline: str = "schema-7",
    review: str = "git:abc",
    step: str = "STEP_01.md",
) -> str:
    return (
        f"- Phase state: {phase_state}\n"
        f"- Handoff schema version: {schema}\n"
        f"- Current executable step: `{step}`\n"
        f"- Current STEP checkpoint: `{checkpoint}`\n"
        f"- Schema/migration version: {baseline}\n"
        f"- Repository/worktree checkpoint reviewed: {review}\n"
        f"- Result: {result}\n"
    )


def step_text_v2() -> str:
    return (
        "# STEP_01: example\n\n"
        "## Outcome\n\n- Deliver one verified example.\n"
        "\n## Contract references and delta\n\n"
        "| Contract ID | Delta |\n"
        "|---|---|\n"
        "| `INV-01` | unchanged |\n"
        "\n## File boundary\n\n- Modify only `example.py`.\n"
        "\n## Risk controls\n\n- Active packs: none.\n"
        "\n## Acceptance\n\n- Run `python -m unittest`.\n"
        "\n## Stop conditions\n\n- Stop when scope is insufficient.\n"
    )


def registry_text_v2() -> str:
    return (
        "# Phase example\n\n"
        "## Contract registry\n\n"
        "| ID | Kind | Authority | Guard | Rule |\n"
        "|---|---|---|---|---|\n"
        "| `INV-01` | invariant | `example.py:run` | `test_example.py` | Stable |\n"
    )


def status_text_v2(
    checkpoint: str,
    registry_checkpoint: str,
    *,
    result: str = "PASS",
    phase_state: str = "in progress",
) -> str:
    manifest = {
        "handoff_schema": 2,
        "phase_state": phase_state,
        "current_step": "STEP_01.md",
        "step_sha256": checkpoint,
        "contract_registry": "README.md",
        "contract_registry_sha256": registry_checkpoint,
        "review_result": result,
        "repository": {"mode": "manual", "checkpoint": "snapshot:contract-test"},
    }
    return (
        "# Phase example current status\n\n"
        "```json phase-handoff\n"
        f"{json.dumps(manifest, indent=2)}\n"
        "```\n"
    )


def validate_static_contract() -> bool:
    status_template = (PLANNER / "assets" / "STATUS_TEMPLATE.md").read_text(encoding="utf-8")
    step_template = (PLANNER / "assets" / "STEP_TEMPLATE.md").read_text(encoding="utf-8")
    require(
        status_template,
        (
            "```json phase-handoff",
            '"handoff_schema": 2',
            '"step_sha256": "AUTO"',
            '"contract_registry_sha256": "AUTO"',
            '"mode": "git"',
            "let `--prepare` generate digests and Git facts",
            "`--dry-run` preflight",
        ),
        PLANNER / "assets" / "STATUS_TEMPLATE.md",
    )
    require(
        step_template,
        (
            "## Contract references and delta",
            "## File boundary",
            "## Risk controls",
            "## Acceptance",
            "## Stop conditions",
            "FAILURE_PATTERNS.md",
        ),
        PLANNER / "assets" / "STEP_TEMPLATE.md",
    )
    if not EXECUTOR_HANDOFF.is_file():
        return False
    executor = EXECUTOR_HANDOFF.read_text(encoding="utf-8")
    require(
        executor,
        (
            "handoff schema `1` or `2`",
            "schema 2",
            "schema 1",
            "deprecated",
            "live Git",
            "`STALE` and `BLOCKED` are not executable",
            "`development complete` and `accepted` are not executable",
            "unresolved bundled template placeholders",
            "Contract references and delta",
            "Risk controls",
        ),
        EXECUTOR_HANDOFF,
    )
    return True


def validate_scenarios() -> None:
    validator = load_validator()
    with tempfile.TemporaryDirectory(prefix="handoff-contract-") as temporary:
        phase = Path(temporary).resolve()
        step = phase / "STEP_01.md"
        status = phase / "STATUS.md"
        registry = phase / "README.md"
        registry.write_text(registry_text_v2(), encoding="utf-8")
        registry_checkpoint = validator.sha256(registry)

        step.write_text(step_text(), encoding="utf-8")
        digest = validator.sha256(step)
        status.write_text(status_text(digest), encoding="utf-8")
        validator.validate(phase)

        step.write_text(step_text_v2(), encoding="utf-8")
        digest_v2 = validator.sha256(step)
        status.write_text(
            status_text_v2(digest_v2, registry_checkpoint),
            encoding="utf-8",
        )
        validator.validate(phase)

        incomplete_v2 = step_text_v2().replace(
            "\n## Risk controls\n\n- Active packs: none.\n",
            "",
        )
        step.write_text(incomplete_v2, encoding="utf-8")
        status.write_text(
            status_text_v2(validator.sha256(step), registry_checkpoint),
            encoding="utf-8",
        )
        expect_rejected(lambda: validator.validate(phase), "## Risk controls section")

        step.write_text(step_text_v2(), encoding="utf-8")
        digest_v2 = validator.sha256(step)
        status.write_text(
            status_text_v2(digest_v2, registry_checkpoint, result="STALE"),
            encoding="utf-8",
        )
        expect_rejected(lambda: validator.validate(phase), "not executable: STALE")

        status.write_text(
            status_text_v2("sha256:" + "0" * 64, registry_checkpoint),
            encoding="utf-8",
        )
        expect_rejected(lambda: validator.validate(phase), "current STEP checkpoint mismatch")

        step.write_text(step_text(), encoding="utf-8")
        incomplete = step_text().replace(
            "\n## File boundary\n\n- Modify only `example.py`.\n",
            "",
        )
        step.write_text(incomplete, encoding="utf-8")
        incomplete_digest = validator.sha256(step)
        status.write_text(status_text(incomplete_digest), encoding="utf-8")
        expect_rejected(lambda: validator.validate(phase), "## File boundary section")

        step.write_text(step_text(), encoding="utf-8")
        digest = validator.sha256(step)

        status.write_text(status_text(digest, schema="2"), encoding="utf-8")
        expect_rejected(lambda: validator.validate(phase), "unsupported or mixed handoff schema")

        status.write_text(status_text(digest, result="STALE"), encoding="utf-8")
        expect_rejected(lambda: validator.validate(phase), "not executable: STALE")

        status.write_text(status_text(digest, result="BLOCKED"), encoding="utf-8")
        expect_rejected(lambda: validator.validate(phase), "not executable: BLOCKED")

        status.write_text(status_text(digest, phase_state="accepted"), encoding="utf-8")
        expect_rejected(lambda: validator.validate(phase), "phase state is not executable: accepted")

        status.write_text(status_text(digest, phase_state="development complete"), encoding="utf-8")
        expect_rejected(
            lambda: validator.validate(phase),
            "phase state is not executable: development complete",
        )

        step.write_text(step_text(review="BLOCKED"), encoding="utf-8")
        blocked_review_digest = validator.sha256(step)
        status.write_text(status_text(blocked_review_digest), encoding="utf-8")
        expect_rejected(
            lambda: validator.validate(phase),
            "STEP pre-step consistency review is not executable: BLOCKED",
        )

        step.write_text(step_text(), encoding="utf-8")
        digest = validator.sha256(step)

        status.write_text(
            status_text(digest, baseline="{{SCHEMA_VERSION}}"),
            encoding="utf-8",
        )
        expect_rejected(lambda: validator.validate(phase), "unresolved bundled template placeholders")

        status.write_text(status_text(digest, baseline="schema-8"), encoding="utf-8")
        expect_rejected(lambda: validator.validate(phase), "baseline mismatch")

        status.write_text(status_text(digest, review="git:def"), encoding="utf-8")
        expect_rejected(lambda: validator.validate(phase), "checkpoint mismatch")

        status.write_text(status_text("sha256:" + "0" * 64), encoding="utf-8")
        expect_rejected(lambda: validator.validate(phase), "current STEP checkpoint mismatch")

        status.write_text(status_text(digest).replace("- Result: PASS\n", ""), encoding="utf-8")
        expect_rejected(lambda: validator.validate(phase), "pre-step consistency Result")

        outside = phase.parent / f"{phase.name}-outside.md"
        try:
            outside.write_text(step_text(), encoding="utf-8")
            status.write_text(
                status_text(validator.sha256(outside), step=f"../{outside.name}"),
                encoding="utf-8",
            )
            expect_rejected(lambda: validator.validate(phase), "escapes the phase directory")
        finally:
            outside.unlink(missing_ok=True)


def main() -> int:
    executor_checked = validate_static_contract()
    validate_scenarios()
    if executor_checked:
        print("PASS: planner and executor satisfy handoff schemas 1 and 2")
    else:
        print("PASS: planner handoff schemas 1 and 2 are internally consistent")
        print("NOT_APPLICABLE: adjacent deliver-code-change integration was not installed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
