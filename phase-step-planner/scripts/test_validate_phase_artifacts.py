from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from validate_phase_artifacts import (
    REQUIRED_STATUS_LABELS,
    REQUIRED_STEP_HEADINGS,
    sha256_checkpoint,
    validate_phase,
)


STEP_BODY = """# STEP_001: Freeze contract

## One outcome
Freeze the interface.
## Non-goals
- Adapter work
## Entry conditions and verified baseline
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
        self.assertIn("| Step document |", readme_template)

    def make_phase(
        self,
        *,
        step_text: str = STEP_BODY,
        current: str = "STEP_001_freeze_contract.md",
        recorded_checkpoint: str | None = None,
        extra_row: str = "",
        phase_state: str = "in-progress",
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
            "- Verified Git checkpoint: `abc123`\n"
            "- Worktree state: clean\n"
            f"- Phase state: {phase_state}\n"
            f"- Current executable step: `{current}`\n"
            f"- Current step specification checkpoint: `{value}`\n"
            "- Audited against repository checkpoint: `abc123`\n",
            encoding="utf-8",
        )
        return root

    def test_valid_phase_passes(self) -> None:
        self.assertEqual(validate_phase(self.make_phase()), [])

    def test_unresolved_placeholder_fails(self) -> None:
        errors = validate_phase(self.make_phase(step_text=STEP_BODY + "\n{{LEFTOVER}}\n"))
        self.assertTrue(any("unresolved placeholders" in error for error in errors))

    def test_checkpoint_mismatch_fails(self) -> None:
        errors = validate_phase(self.make_phase(recorded_checkpoint="sha256:" + "0" * 64))
        self.assertTrue(any("checkpoint mismatch" in error for error in errors))

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
        status.write_text(status_text, encoding="utf-8")
        readme = root.joinpath("README.md")
        readme.write_text(
            readme.read_text(encoding="utf-8").replace("| detailed |", "| accepted |"),
            encoding="utf-8",
        )
        self.assertEqual(validate_phase(root), [])


if __name__ == "__main__":
    unittest.main()
