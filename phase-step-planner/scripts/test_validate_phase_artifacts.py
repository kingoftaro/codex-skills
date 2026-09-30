from __future__ import annotations

import json
import io
import re
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from validate_phase_artifacts import (
    REQUIRED_STATUS_LABELS,
    REQUIRED_STEP_HEADINGS,
    inspect_phase,
    main,
    read_utf8,
    sha256_checkpoint,
    validate_phase,
)


def repair_loop(
    state: str = "inactive",
    *,
    invariant_id: str = "none",
    consecutive_regressions: int = 0,
    last_classification: str = "none",
    evidence: str = "none",
) -> str:
    return json.dumps(
        {
            "state": state,
            "invariant_id": invariant_id,
            "consecutive_regressions": consecutive_regressions,
            "last_classification": last_classification,
            "evidence": evidence,
        },
        separators=(",", ":"),
    )


INACTIVE_REPAIR_LOOP = repair_loop()


STEP_BODY = """# STEP_001: Freeze contract

## One outcome
Freeze the interface.
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
Report touchpoints.
## Acceptance
- Contract test passes
## Stop and degrade
- Stop on incompatible caller
## Deliverables
- Contract and tests
"""


class ValidatePhaseArtifactsTests(unittest.TestCase):
    def test_bundled_templates_match_validator_contract(self) -> None:
        skill_root = Path(__file__).resolve().parent.parent
        status_template = skill_root.joinpath("assets", "STATUS_TEMPLATE.md").read_text(
            encoding="utf-8"
        )
        step_template = skill_root.joinpath("assets", "STEP_TEMPLATE.md").read_text(
            encoding="utf-8"
        )
        readme_template = skill_root.joinpath("assets", "PHASE_README_TEMPLATE.md").read_text(
            encoding="utf-8"
        )
        for label in REQUIRED_STATUS_LABELS:
            self.assertIn(f"- {label}:", status_template)
        for heading in REQUIRED_STEP_HEADINGS:
            self.assertIn(heading, step_template.splitlines())
        self.assertIn("- Handoff schema: 1", step_template)
        self.assertIn("- Review route: {{FAST_STANDARD_OR_HIGH_RISK}}", step_template)
        self.assertNotIn("- Transaction/CAS/version rule:", step_template)
        self.assertNotIn("## Implementation order", step_template)
        self.assertIn("| Step document |", readme_template)

    def make_phase(
        self,
        *,
        step_text: str = STEP_BODY,
        current: str = "STEP_001_freeze_contract.md",
        recorded_checkpoint: str | None = None,
        extra_row: str = "",
        phase_state: str = "in-progress",
        handoff_schema: str = "1",
        review_result: str = "PASS",
        repair_loop_value: str = INACTIVE_REPAIR_LOOP,
        audited_checkpoint: str = "abc123",
    ) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        step_path = root / "STEP_001_freeze_contract.md"
        step_path.write_text(step_text, encoding="utf-8")
        root.joinpath("README.md").write_text(
            "# Phase P1 implementation index\n\n"
            "| Step document | One outcome | Depends on | Primary risk boundary | Specification state |\n"
            "|---|---|---|---|---|\n"
            "| `STEP_001_freeze_contract.md` | Freeze contract | none | compatibility | detailed |\n"
            f"{extra_row}",
            encoding="utf-8",
        )
        value = recorded_checkpoint or sha256_checkpoint(step_path)
        root.joinpath("STATUS.md").write_text(
            "# Phase P1 current status\n\n"
            f"- Handoff schema: {handoff_schema}\n"
            f"- Review result: {review_result}\n"
            f"- Repair loop: `{repair_loop_value}`\n"
            "- Verified Git checkpoint: `abc123`\n"
            "- Worktree state: clean\n"
            f"- Phase state: {phase_state}\n"
            f"- Current executable step: `{current}`\n"
            f"- Current step specification checkpoint: `{value}`\n"
            f"- Audited against repository checkpoint: `{audited_checkpoint}`\n",
            encoding="utf-8",
        )
        return root

    def test_valid_phase_passes(self) -> None:
        self.assertEqual(validate_phase(self.make_phase()), [])

    def test_generated_templates_validate(self) -> None:
        root = self.make_phase()
        assets = Path(__file__).resolve().parent.parent / "assets"
        values = {"STEP_DOCUMENT": "STEP_001_freeze_contract.md",
                  "CURRENT_STEP_DOCUMENT": "STEP_001_freeze_contract.md",
                  "FAST_STANDARD_OR_HIGH_RISK": "Fast",
                  "COMMIT_OR_UNCOMMITTED_EXPLANATION": "abc123",
                  "AUDITED_REPOSITORY_CHECKPOINT": "abc123"}

        def render(name: str) -> str:
            return re.sub(r"\{\{([A-Z][A-Z0-9_]*)\}\}",
                          lambda match: values.get(match[1], "none"),
                          assets.joinpath(name).read_text(encoding="utf-8"))

        step = root / "STEP_001_freeze_contract.md"
        step.write_text(render("STEP_TEMPLATE.md"), encoding="utf-8")
        values["CURRENT_STEP_SHA256"] = sha256_checkpoint(step).removeprefix("sha256:")
        root.joinpath("STATUS.md").write_text(
            render("STATUS_TEMPLATE.md")
            .replace("PASS / STALE / BLOCKED / NOT_APPLICABLE", "PASS")
            .replace("not-started / in-progress / development-complete / accepted / release-ready / release-blocked", "in-progress"),
            encoding="utf-8",
        )
        root.joinpath("README.md").write_text(
            render("PHASE_README_TEMPLATE.md").replace("detailed / outline / accepted / deferred", "detailed"),
            encoding="utf-8",
        )
        self.assertEqual(validate_phase(root), [])

    def test_unrelated_drafts_and_history_do_not_block(self) -> None:
        root = self.make_phase(extra_row="| `STEP_002_draft.md` | Later | STEP_001 | none | outline |\n")
        root.joinpath("STEP_002_draft.md").write_text("{{LATER_OUTCOME}}", encoding="utf-8")
        root.joinpath("HISTORY.md").write_bytes(b"\xff{{OLD_NOTE}}")
        self.assertEqual(validate_phase(root), [])

    def test_authoritative_status_and_index_placeholders_block(self) -> None:
        for name in ("STATUS.md", "README.md"):
            with self.subTest(name=name):
                root = self.make_phase()
                path = root / name
                path.write_text(path.read_text(encoding="utf-8") + "\n{{LEFTOVER}}\n", encoding="utf-8")
                result = inspect_phase(root)
                self.assertEqual(result.outcome, "FAIL")
                self.assertTrue(any(name in error and "unresolved placeholders" in error for error in result.errors))

    def test_expected_code_edit_does_not_invalidate_document_checkpoint(self) -> None:
        root = self.make_phase()
        root.joinpath("src").mkdir()
        root.joinpath("src", "contract.py").write_text("result = 1\n", encoding="utf-8")
        self.assertEqual(validate_phase(root), [])

    def run_cli(self, root: Path, *options: str) -> tuple[int, str]:
        output = io.StringIO()
        with redirect_stdout(output):
            exit_code = main([str(root), *options])
        return exit_code, output.getvalue()

    def test_cli_distinguishes_stale_blocked_and_structural_failure(self) -> None:
        for review, expected in (("STALE", "STALE"), ("BLOCKED", "BLOCKED"), ("invalid", "FAIL")):
            with self.subTest(review=review):
                root = self.make_phase(review_result=review)
                before = root.joinpath("STATUS.md").read_bytes()
                code, output = self.run_cli(root)
                self.assertEqual(code, 1)
                self.assertIn(f"{expected}: handoff is not executable", output)
                self.assertEqual(root.joinpath("STATUS.md").read_bytes(), before)

    def test_digest_mismatch_requires_classification_and_remains_nonexecutable(self) -> None:
        root = self.make_phase(recorded_checkpoint="sha256:" + "0" * 64)
        code, output = self.run_cli(root)
        self.assertEqual(code, 1)
        self.assertIn("STALE: handoff is not executable", output)
        self.assertIn("does not determine its origin", output)
        self.assertNotIn("BLOCKED: handoff", output)

    def test_recorded_baseline_conflict_is_blocked(self) -> None:
        root = self.make_phase(audited_checkpoint="different")
        code, output = self.run_cli(root)
        self.assertEqual(code, 1)
        self.assertIn("BLOCKED: handoff is not executable", output)

    def test_structure_failure_takes_priority_over_pending_sync(self) -> None:
        root = self.make_phase(step_text=STEP_BODY + "\n{{LEFTOVER}}\n", review_result="STALE")
        code, output = self.run_cli(root)
        self.assertEqual(code, 1)
        self.assertIn("FAIL: handoff is not executable", output)

    def test_optional_directory_hygiene_is_advisory(self) -> None:
        root = self.make_phase()
        root.joinpath("STEP_002_draft.md").write_text("{{LATER_OUTCOME}}", encoding="utf-8")
        code, output = self.run_cli(root, "--check-all-docs")
        self.assertEqual(code, 0)
        self.assertIn("WARNING: unresolved placeholders in STEP_002_draft.md", output)
        self.assertIn("PASS:", output)

    def test_directory_hygiene_does_not_override_current_errors(self) -> None:
        root = self.make_phase(step_text=STEP_BODY + "\n{{LEFTOVER}}\n")
        code, output = self.run_cli(root, "--check-all-docs")
        self.assertEqual(code, 1)
        self.assertIn("FAIL: handoff is not executable", output)

    def test_unreadable_optional_document_is_only_a_warning(self) -> None:
        root = self.make_phase()
        root.joinpath("DRAFT.md").write_text("draft", encoding="utf-8")

        def controlled_read(path: Path, issues: list[str]) -> str:
            if path.name == "DRAFT.md":
                raise PermissionError("controlled unreadable fixture")
            return read_utf8(path, issues)

        with patch("validate_phase_artifacts.read_utf8", side_effect=controlled_read):
            code, output = self.run_cli(root, "--check-all-docs")
        self.assertEqual(code, 0)
        self.assertIn("WARNING: could not read optional document DRAFT.md", output)
        self.assertIn("PASS:", output)

    def test_non_pass_handoff_is_not_executable(self) -> None:
        for review_result in ("STALE", "BLOCKED", "NOT_APPLICABLE"):
            with self.subTest(review_result=review_result):
                errors = validate_phase(self.make_phase(review_result=review_result))
                self.assertTrue(any("not executable" in error for error in errors))

    def test_observing_repair_loop_passes_structural_validation(self) -> None:
        observing = repair_loop(
            "observing",
            invariant_id="INV-1",
            consecutive_regressions=1,
            last_classification="repair-introduced",
            evidence="STATUS.md#repair-1",
        )
        self.assertEqual(validate_phase(self.make_phase(repair_loop_value=observing)), [])

    def test_blocked_repair_loop_requires_blocked_review(self) -> None:
        blocked = repair_loop(
            "blocked",
            invariant_id="INV-1",
            consecutive_regressions=2,
            last_classification="repair-introduced",
            evidence="STATUS.md#repair-2",
        )
        errors = validate_phase(self.make_phase(repair_loop_value=blocked))
        self.assertIn("blocked Repair loop requires Review result `BLOCKED`", errors)

    def test_second_regression_cannot_remain_observing(self) -> None:
        observing = repair_loop(
            "observing",
            invariant_id="INV-1",
            consecutive_regressions=2,
            last_classification="repair-introduced",
            evidence="STATUS.md#repair-2",
        )
        errors = validate_phase(self.make_phase(repair_loop_value=observing))
        self.assertIn("observing Repair loop must have exactly one consecutive regression", errors)

    def test_reset_repair_loop_requires_root_cause_evidence(self) -> None:
        reset = repair_loop(
            "reset",
            invariant_id="INV-1",
            last_classification="repair-introduced",
        )
        errors = validate_phase(self.make_phase(repair_loop_value=reset))
        self.assertIn("reset Repair loop requires invariant_id and root-cause evidence", errors)

    def test_evidenced_reset_repair_loop_passes_structural_validation(self) -> None:
        reset = repair_loop(
            "reset",
            invariant_id="INV-1",
            last_classification="repair-introduced",
            evidence="STATUS.md#root-cause-review",
        )
        self.assertEqual(validate_phase(self.make_phase(repair_loop_value=reset)), [])

    def test_malformed_repair_loop_fails(self) -> None:
        errors = validate_phase(self.make_phase(repair_loop_value="{not-json"))
        self.assertTrue(any("invalid Repair loop JSON" in error for error in errors))

    def test_unknown_handoff_schema_fails(self) -> None:
        errors = validate_phase(self.make_phase(handoff_schema="99"))
        self.assertTrue(any("unsupported or missing Handoff schema" in error for error in errors))

    def test_status_and_step_schema_must_match(self) -> None:
        errors = validate_phase(
            self.make_phase(step_text=STEP_BODY.replace("Handoff schema: 1", "Handoff schema: 2"))
        )
        self.assertTrue(any("handoff schemas do not match" in error for error in errors))

    def test_unresolved_placeholder_fails(self) -> None:
        errors = validate_phase(self.make_phase(step_text=STEP_BODY + "\n{{LEFTOVER}}\n"))
        self.assertTrue(any("unresolved placeholders" in error for error in errors))

    def test_checkpoint_mismatch_fails(self) -> None:
        errors = validate_phase(self.make_phase(recorded_checkpoint="sha256:" + "0" * 64))
        mismatch = next(error for error in errors if "checkpoint mismatch" in error)
        self.assertIn("STALE", mismatch)
        self.assertIn("BLOCKED", mismatch)

    def test_reviewed_and_audited_checkpoints_must_match(self) -> None:
        errors = validate_phase(self.make_phase(audited_checkpoint="different"))
        self.assertTrue(any("audited repository checkpoint do not match" in error for error in errors))

    def test_step_change_after_snapshot_fails(self) -> None:
        root = self.make_phase()
        root.joinpath("STEP_001_freeze_contract.md").write_text(
            STEP_BODY + "\nChanged after STATUS was written.\n", encoding="utf-8"
        )
        errors = validate_phase(root)
        self.assertTrue(any("checkpoint mismatch" in error for error in errors))

    def test_duplicate_detailed_steps_fail(self) -> None:
        errors = validate_phase(
            self.make_phase(
                extra_row="| `STEP_002_adapter.md` | Add adapter | STEP_001 | network | detailed |\n"
            )
        )
        self.assertTrue(any("exactly one detailed step" in error for error in errors))

    def test_current_step_must_match_detailed_row(self) -> None:
        errors = validate_phase(self.make_phase(current="STEP_002_adapter.md"))
        self.assertTrue(any("does not match Current executable step" in error for error in errors))

    def test_path_escape_is_rejected(self) -> None:
        errors = validate_phase(self.make_phase(current="../STEP_001.md"))
        self.assertTrue(any("safe relative path" in error for error in errors))

    def test_missing_required_status_field_fails(self) -> None:
        root = self.make_phase()
        status = root.joinpath("STATUS.md")
        status.write_text(
            status.read_text(encoding="utf-8").replace("- Worktree state: clean\n", ""),
            encoding="utf-8",
        )
        errors = validate_phase(root)
        self.assertIn("missing required STATUS field: Worktree state", errors)

    def test_empty_required_step_section_fails(self) -> None:
        empty = STEP_BODY.replace("## Acceptance\n- Contract test passes", "## Acceptance")
        errors = validate_phase(self.make_phase(step_text=empty))
        self.assertTrue(any("empty required sections" in error for error in errors))

    def test_duplicate_required_step_heading_fails(self) -> None:
        duplicate = STEP_BODY + "\n## Acceptance\n- Duplicate acceptance\n"
        errors = validate_phase(self.make_phase(step_text=duplicate))
        self.assertTrue(any("duplicate required headings" in error for error in errors))

    def test_terminal_phase_without_current_step_passes(self) -> None:
        root = self.make_phase(phase_state="accepted")
        status = root.joinpath("STATUS.md")
        status_text = status.read_text(encoding="utf-8")
        status_text = status_text.replace(
            "- Current executable step: `STEP_001_freeze_contract.md`",
            "- Current executable step: `none`",
        )
        status_text = status_text.replace(
            f"- Current step specification checkpoint: `{sha256_checkpoint(root / 'STEP_001_freeze_contract.md')}`",
            "- Current step specification checkpoint: `not-applicable`",
        )
        status_text = status_text.replace("- Review result: PASS", "- Review result: NOT_APPLICABLE")
        status.write_text(status_text, encoding="utf-8")
        readme = root.joinpath("README.md")
        readme.write_text(
            readme.read_text(encoding="utf-8").replace("| detailed |", "| accepted |"),
            encoding="utf-8",
        )
        self.assertEqual(validate_phase(root), [])


if __name__ == "__main__":
    unittest.main()
