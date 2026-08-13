#!/usr/bin/env python3
"""Validate the planner/executor handoff contract and adversarial cases."""

from __future__ import annotations

import importlib.util
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


def step_text(schema: str = "1", baseline: str = "schema-7", review: str = "git:abc") -> str:
    return (
        "# STEP_01: example\n\n"
        f"- Handoff schema version: {schema}\n"
        f"- Current schema/migration: {baseline}\n"
        f"- Reviewed repository/worktree checkpoint: {review}\n"
    )


def status_text(
    checkpoint: str,
    *,
    schema: str = "1",
    result: str = "PASS",
    baseline: str = "schema-7",
    review: str = "git:abc",
    step: str = "STEP_01.md",
) -> str:
    return (
        f"- Handoff schema version: {schema}\n"
        f"- Current executable step: `{step}`\n"
        f"- Current STEP checkpoint: `{checkpoint}`\n"
        f"- Schema/migration version: {baseline}\n"
        f"- Repository/worktree checkpoint reviewed: {review}\n"
        f"- Result: {result}\n"
    )


def validate_static_contract() -> bool:
    status_template = (PLANNER / "assets" / "STATUS_TEMPLATE.md").read_text(encoding="utf-8")
    step_template = (PLANNER / "assets" / "STEP_TEMPLATE.md").read_text(encoding="utf-8")
    require(
        status_template,
        (
            "Handoff schema version: 1",
            "Current STEP checkpoint:",
            "Schema/migration version:",
            "Repository/worktree checkpoint reviewed:",
            "Result: {{PASS_STALE_OR_BLOCKED}}",
            "| Interface | Authority | Producer | Consumers | Version/hash | Compatibility |",
        ),
        PLANNER / "assets" / "STATUS_TEMPLATE.md",
    )
    require(
        step_template,
        (
            "Handoff schema version: 1",
            "Current schema/migration:",
            "Reviewed repository/worktree checkpoint:",
            "Pre-step consistency review: PASS",
        ),
        PLANNER / "assets" / "STEP_TEMPLATE.md",
    )
    if not EXECUTOR_HANDOFF.is_file():
        return False
    executor = EXECUTOR_HANDOFF.read_text(encoding="utf-8")
    require(
        executor,
        (
            "handoff schema version `1`",
            "`STALE` and `BLOCKED` are not executable",
            "same schema/migration baseline",
            "same schema/migration baseline and reviewed repository/worktree checkpoint",
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

        step.write_text(step_text(), encoding="utf-8")
        digest = validator.sha256(step)
        status.write_text(status_text(digest), encoding="utf-8")
        validator.validate(phase)

        status.write_text(status_text(digest, schema="2"), encoding="utf-8")
        expect_rejected(lambda: validator.validate(phase), "unsupported or mixed handoff schema")

        status.write_text(status_text(digest, result="STALE"), encoding="utf-8")
        expect_rejected(lambda: validator.validate(phase), "not executable: STALE")

        status.write_text(status_text(digest, result="BLOCKED"), encoding="utf-8")
        expect_rejected(lambda: validator.validate(phase), "not executable: BLOCKED")

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
        print("PASS: planner and executor satisfy handoff schema version 1")
    else:
        print("PASS: planner handoff schema version 1 is internally consistent")
        print("NOT_APPLICABLE: adjacent deliver-code-change integration was not installed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
