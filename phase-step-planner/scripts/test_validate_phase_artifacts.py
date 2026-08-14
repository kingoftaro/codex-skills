from __future__ import annotations

import importlib.util
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


if __name__ == "__main__":
    unittest.main()
