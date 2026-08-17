from __future__ import annotations

import importlib.util
import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path


VALIDATOR_PATH = Path(__file__).with_name("validate_phase_artifacts.py")
SPEC = importlib.util.spec_from_file_location("phase_artifact_validator_tests", VALIDATOR_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load validator: {VALIDATOR_PATH}")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


def step_text(
    *,
    baseline: str = "schema-7",
    checkpoint: str = "git:abc",
    review: str = "PASS",
    extra: str = "",
) -> str:
    return (
        "# STEP_01: example\n\n"
        "## Handoff contract\n\n"
        "- Handoff schema version: 1\n"
        f"- Current schema/migration: {baseline}\n"
        f"- Reviewed repository/worktree checkpoint: {checkpoint}\n"
        f"- Pre-step consistency review: {review}\n"
        "\n## One outcome\n\n"
        "- Deliver one verified example.\n"
        "\n## Non-goals\n\n"
        "- Do not change unrelated behavior.\n"
        "\n## Entry conditions and verified baseline\n\n"
        "- Baseline command: `python -V` -> PASS.\n"
        "\n## File boundary\n\n"
        "| Access | Path | Purpose |\n"
        "|---|---|---|\n"
        "| Modify | `example.py` | Implement the example |\n"
        "\n## Contracts and invariants\n\n"
        "- Preserve the example contract.\n"
        "\n## Side-effect policy\n\n"
        "- No external effects are allowed.\n"
        "\n## Implementation order\n\n"
        "1. Implement the example.\n"
        "2. Run the checks.\n"
        "\n## Required pre-code rehearsal\n\n"
        "- Trace the example call path before editing.\n"
        "\n## Acceptance\n\n"
        "### Normal cases\n\n"
        "- The example succeeds.\n"
        "\n### Failure and adversarial cases\n\n"
        "- Invalid input is rejected.\n"
        "\n### Validation commands\n\n"
        "- Run `python -m unittest`.\n"
        "\n## Stop and degrade\n\n"
        "- Stop if the file boundary is insufficient.\n"
        "\n## Deliverables\n\n"
        "- Code and test evidence.\n"
        f"{extra}"
    )


def status_text(
    digest: str,
    *,
    phase_state: str = "in progress",
    baseline: str = "schema-7",
    checkpoint: str = "git:abc",
    result: str = "PASS",
) -> str:
    return (
        f"- Phase state: {phase_state}\n"
        "- Handoff schema version: 1\n"
        "- Current executable step: `STEP_01.md`\n"
        f"- Current STEP checkpoint: `{digest}`\n"
        f"- Schema/migration version: {baseline}\n"
        f"- Repository/worktree checkpoint reviewed: {checkpoint}\n"
        f"- Result: {result}\n"
    )


def step_text_v2(*, extra: str = "") -> str:
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
        "\n## Stop conditions\n\n- Stop if the file boundary is insufficient.\n"
        f"{extra}"
    )


def registry_text_v2() -> str:
    return (
        "# Phase example\n\n"
        "## Contract registry\n\n"
        "| ID | Kind | Authority | Guard | Rule |\n"
        "|---|---|---|---|---|\n"
        "| `INV-01` | invariant | `example.py:run` | `test_example.py` | Stable |\n"
    )


def registry_digest_v2() -> str:
    serialized = registry_text_v2().replace("\n", os.linesep).encode("utf-8")
    digest = hashlib.sha256(serialized).hexdigest()
    return f"sha256:{digest}"


def status_text_v2(
    digest: str,
    *,
    phase_state: str = "in progress",
    result: str = "PASS",
    step: str = "STEP_01.md",
    repository: dict[str, str] | None = None,
) -> str:
    manifest = {
        "handoff_schema": 2,
        "phase_state": phase_state,
        "current_step": step,
        "step_sha256": digest,
        "contract_registry": "README.md",
        "contract_registry_sha256": registry_digest_v2(),
        "review_result": result,
        "repository": repository
        or {"mode": "manual", "checkpoint": "snapshot:test-fixture"},
    }
    return (
        "# Phase test current status\n\n"
        "```json phase-handoff\n"
        f"{json.dumps(manifest, indent=2)}\n"
        "```\n"
    )


class PhaseArtifactValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="phase-artifact-test-")
        self.phase = Path(self.temporary.name)
        self.step = self.phase / "STEP_01.md"
        self.status = self.phase / "STATUS.md"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_handoff(
        self,
        *,
        phase_state: str = "in progress",
        baseline: str = "schema-7",
        review: str = "PASS",
        extra_step: str = "",
    ) -> None:
        self.step.write_text(
            step_text(baseline=baseline, review=review, extra=extra_step),
            encoding="utf-8",
        )
        self.status.write_text(
            status_text(
                VALIDATOR.sha256(self.step),
                phase_state=phase_state,
                baseline=baseline,
            ),
            encoding="utf-8",
        )

    def assert_rejected(self, expected: str) -> None:
        with self.assertRaisesRegex(ValueError, expected):
            VALIDATOR.validate(self.phase)

    def test_active_phase_states_are_executable(self) -> None:
        for state in ("not started", "in progress", "release blocked"):
            with self.subTest(state=state):
                self.write_handoff(phase_state=state)
                VALIDATOR.validate(self.phase)

    def test_terminal_phase_states_are_rejected(self) -> None:
        for state in ("development complete", "accepted"):
            with self.subTest(state=state):
                self.write_handoff(phase_state=state)
                self.assert_rejected(f"phase state is not executable: {state}")

    def test_unknown_phase_state_is_rejected(self) -> None:
        self.write_handoff(phase_state="paused")
        self.assert_rejected("unsupported phase state: paused")

    def test_non_pass_step_review_is_rejected(self) -> None:
        self.write_handoff(review="BLOCKED")
        self.assert_rejected("STEP pre-step consistency review is not executable: BLOCKED")

    def test_missing_step_review_is_rejected(self) -> None:
        self.write_handoff()
        text = self.step.read_text(encoding="utf-8").replace(
            "- Pre-step consistency review: PASS\n",
            "",
        )
        self.step.write_text(text, encoding="utf-8")
        self.status.write_text(
            status_text(VALIDATOR.sha256(self.step)),
            encoding="utf-8",
        )
        self.assert_rejected("pre-step consistency review in STEP")

    def test_bundled_template_placeholders_are_rejected(self) -> None:
        self.write_handoff(baseline="{{SCHEMA_VERSION}}")
        self.assert_rejected("unresolved bundled template placeholders")

    def test_step_template_placeholders_are_rejected(self) -> None:
        self.write_handoff(extra_step="- Pending test: {{NORMAL_TEST}}\n")
        self.assert_rejected("unresolved bundled template placeholders")

    def test_missing_required_step_section_is_rejected(self) -> None:
        self.write_handoff()
        text = self.step.read_text(encoding="utf-8").replace(
            "\n## File boundary\n\n"
            "| Access | Path | Purpose |\n"
            "|---|---|---|\n"
            "| Modify | `example.py` | Implement the example |\n",
            "",
        )
        self.step.write_text(text, encoding="utf-8")
        self.status.write_text(status_text(VALIDATOR.sha256(self.step)), encoding="utf-8")
        self.assert_rejected("exactly one ## File boundary section")

    def test_empty_required_step_section_is_rejected(self) -> None:
        self.write_handoff()
        text = self.step.read_text(encoding="utf-8").replace(
            "## One outcome\n\n- Deliver one verified example.\n",
            "## One outcome\n",
        )
        self.step.write_text(text, encoding="utf-8")
        self.status.write_text(status_text(VALIDATOR.sha256(self.step)), encoding="utf-8")
        self.assert_rejected("section ## One outcome has no content")

    def test_missing_acceptance_subsection_is_rejected(self) -> None:
        self.write_handoff()
        text = self.step.read_text(encoding="utf-8").replace(
            "\n### Validation commands\n\n- Run `python -m unittest`.\n",
            "",
        )
        self.step.write_text(text, encoding="utf-8")
        self.status.write_text(status_text(VALIDATOR.sha256(self.step)), encoding="utf-8")
        self.assert_rejected("exactly one ### Validation commands section")

    def test_unrelated_template_syntax_is_allowed(self) -> None:
        self.write_handoff(extra_step="- Application example: {{USER_NAME}}\n")
        VALIDATOR.validate(self.phase)


class PhaseArtifactValidationV2Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="phase-artifact-v2-test-")
        self.phase = Path(self.temporary.name)
        self.step = self.phase / "STEP_01.md"
        self.status = self.phase / "STATUS.md"
        self.registry = self.phase / "README.md"
        self.registry.write_text(registry_text_v2(), encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_handoff(
        self,
        *,
        phase_state: str = "in progress",
        result: str = "PASS",
        extra_step: str = "",
        repository: dict[str, str] | None = None,
    ) -> None:
        self.step.write_text(step_text_v2(extra=extra_step), encoding="utf-8")
        self.status.write_text(
            status_text_v2(
                VALIDATOR.sha256(self.step),
                phase_state=phase_state,
                result=result,
                repository=repository,
            ),
            encoding="utf-8",
        )

    def assert_rejected(self, expected: str, **kwargs: object) -> None:
        with self.assertRaisesRegex(ValueError, expected):
            VALIDATOR.validate(self.phase, **kwargs)

    def test_manual_checkpoint_handoff_is_executable(self) -> None:
        self.write_handoff()
        step, digest = VALIDATOR.validate(self.phase)
        self.assertEqual(step, self.step)
        self.assertEqual(digest, VALIDATOR.sha256(self.step))

    def test_terminal_and_unknown_states_are_rejected(self) -> None:
        for state, expected in (
            ("accepted", "phase state is not executable: accepted"),
            ("paused", "unsupported phase state: paused"),
        ):
            with self.subTest(state=state):
                self.write_handoff(phase_state=state)
                self.assert_rejected(expected)

    def test_stale_and_blocked_reviews_are_rejected(self) -> None:
        for result in ("STALE", "BLOCKED"):
            with self.subTest(result=result):
                self.write_handoff(result=result)
                self.assert_rejected(f"not executable: {result}")

    def test_missing_core_section_is_rejected(self) -> None:
        self.write_handoff()
        text = self.step.read_text(encoding="utf-8").replace(
            "\n## Risk controls\n\n- Active packs: none.\n",
            "",
        )
        self.step.write_text(text, encoding="utf-8")
        self.status.write_text(status_text_v2(VALIDATOR.sha256(self.step)), encoding="utf-8")
        self.assert_rejected("exactly one ## Risk controls section")

    def test_template_placeholder_is_rejected(self) -> None:
        self.write_handoff(extra_step="\n- Pending: {{EXACT_COMMANDS}}\n")
        self.assert_rejected("unresolved bundled template placeholders")

    def test_duplicate_and_malformed_manifests_are_rejected(self) -> None:
        self.write_handoff()
        original = self.status.read_text(encoding="utf-8")
        self.status.write_text(original + original, encoding="utf-8")
        self.assert_rejected("exactly one phase-handoff JSON block")
        self.status.write_text("```json phase-handoff\n{invalid}\n```\n", encoding="utf-8")
        self.assert_rejected("phase-handoff JSON is invalid")

    def test_step_path_must_remain_inside_phase(self) -> None:
        outside = self.phase.parent / f"{self.phase.name}-outside.md"
        try:
            outside.write_text(step_text_v2(), encoding="utf-8")
            self.status.write_text(
                status_text_v2(VALIDATOR.sha256(outside), step=f"../{outside.name}"),
                encoding="utf-8",
            )
            self.assert_rejected("escapes the phase directory")
        finally:
            outside.unlink(missing_ok=True)

    def test_prepare_populates_digest_and_git_snapshot_without_processes(self) -> None:
        self.step.write_text(step_text_v2(), encoding="utf-8")
        self.status.write_text(
            status_text_v2(
                "AUTO",
                repository={
                    "mode": "git",
                    "head": "AUTO",
                    "worktree_sha256": "AUTO",
                },
            ),
            encoding="utf-8",
        )
        snapshot = {
            "head": "a" * 40,
            "worktree_sha256": "sha256:" + "b" * 64,
        }
        calls: list[tuple[Path, Path, Path]] = []

        def fake_provider(phase: Path, status: Path, step: Path) -> dict[str, str]:
            calls.append((phase, status, step))
            return snapshot.copy()

        prepared_step, digest = VALIDATOR.prepare(
            self.phase,
            snapshot_provider=fake_provider,
        )
        self.assertEqual(prepared_step, self.step)
        self.assertEqual(digest, VALIDATOR.sha256(self.step))
        manifest, _ = VALIDATOR.phase_manifest(self.status.read_text(encoding="utf-8"))
        self.assertEqual(manifest["step_sha256"], digest)
        self.assertEqual(manifest["repository"]["head"], snapshot["head"])
        self.assertIn("prepared_at", manifest)
        self.assertGreaterEqual(len(calls), 2)

    def test_live_git_drift_is_rejected_with_injected_snapshot(self) -> None:
        expected = {
            "mode": "git",
            "head": "a" * 40,
            "worktree_sha256": "sha256:" + "b" * 64,
        }
        self.write_handoff(repository=expected)

        def changed_worktree(_phase: Path, _status: Path, _step: Path) -> dict[str, str]:
            return {
                "head": "a" * 40,
                "worktree_sha256": "sha256:" + "c" * 64,
            }

        self.assert_rejected(
            "live Git worktree mismatch",
            snapshot_provider=changed_worktree,
        )

    def test_step_digest_drift_is_rejected_before_live_git(self) -> None:
        self.write_handoff()
        self.step.write_text(step_text_v2(extra="\n- Changed.\n"), encoding="utf-8")
        self.assert_rejected("current STEP checkpoint mismatch")

    def test_contract_registry_drift_is_rejected(self) -> None:
        self.write_handoff()
        self.registry.write_text(registry_text_v2() + "\nChanged.\n", encoding="utf-8")
        self.assert_rejected("contract registry checkpoint mismatch")

    def test_unknown_contract_reference_is_rejected(self) -> None:
        self.write_handoff()
        text = self.step.read_text(encoding="utf-8").replace("`INV-01`", "`INV-99`")
        self.step.write_text(text, encoding="utf-8")
        self.status.write_text(status_text_v2(VALIDATOR.sha256(self.step)), encoding="utf-8")
        self.assert_rejected("contract IDs absent from the registry: INV-99")

    def test_unknown_risk_pack_is_rejected(self) -> None:
        self.write_handoff()
        text = self.step.read_text(encoding="utf-8").replace(
            "Active packs: none.",
            "Active packs: `made-up`",
        )
        self.step.write_text(text, encoding="utf-8")
        self.status.write_text(status_text_v2(VALIDATOR.sha256(self.step)), encoding="utf-8")
        self.assert_rejected("unsupported risk packs: made-up")

    def test_contract_ids_allow_explicit_id_bullets(self) -> None:
        text = "## Contract registry\n\n- ID: `interface.user-v2`\n"
        self.assertEqual(
            VALIDATOR.contract_ids(text, "Contract registry", "contract registry"),
            {"interface.user-v2"},
        )

    def test_prepare_rejects_non_pass_review_before_mutation(self) -> None:
        self.step.write_text(step_text_v2(), encoding="utf-8")
        self.status.write_text(
            status_text_v2("AUTO", result="STALE"),
            encoding="utf-8",
        )
        before = self.status.read_bytes()
        with self.assertRaisesRegex(ValueError, "not executable: STALE"):
            VALIDATOR.prepare(self.phase)
        self.assertEqual(self.status.read_bytes(), before)

    def test_git_fingerprint_uses_content_and_excludes_generated_handoff(self) -> None:
        self.step.write_text(step_text_v2(), encoding="utf-8")
        self.status.write_text(status_text_v2("AUTO"), encoding="utf-8")
        extra = self.phase / "extra.txt"
        extra.write_text("one", encoding="utf-8")
        calls: list[tuple[str, ...]] = []

        def fake_runner(_cwd: Path, args: tuple[str, ...]) -> bytes:
            calls.append(args)
            if args == ("rev-parse", "--show-toplevel"):
                return str(self.phase).encode("utf-8") + b"\n"
            if args == ("rev-parse", "HEAD"):
                return b"a" * 40 + b"\n"
            if "diff" in args:
                return b"tracked-diff"
            if args == ("ls-files", "--others", "--exclude-standard", "-z"):
                return b"STATUS.md\0STEP_01.md\0README.md\0extra.txt\0"
            raise AssertionError(f"unexpected Git call: {args}")

        first = VALIDATOR.capture_git_snapshot(
            self.phase,
            self.status,
            self.step,
            runner=fake_runner,
        )
        extra.write_text("two", encoding="utf-8")
        second = VALIDATOR.capture_git_snapshot(
            self.phase,
            self.status,
            self.step,
            runner=fake_runner,
        )
        self.assertNotEqual(first["worktree_sha256"], second["worktree_sha256"])
        diff_call = next(args for args in calls if "diff" in args)
        self.assertIn(":(exclude)STATUS.md", diff_call)
        self.assertIn(":(exclude)STEP_01.md", diff_call)


if __name__ == "__main__":
    unittest.main()
