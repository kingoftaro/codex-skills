from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from validate_handoff_contract import validate_declarations, validate_fixtures


class ValidateHandoffContractTests(unittest.TestCase):
    def make_repository(self) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        source = Path(__file__).resolve().parents[2]
        for name in ("deliver-code-change", "phase-step-planner"):
            shutil.copytree(source / name, root / name,
                            ignore=shutil.ignore_patterns("__pycache__"))
        return root

    def test_bundled_resources_and_fixtures_pass(self) -> None:
        failures, _ = validate_declarations(Path(__file__).resolve().parents[2])
        self.assertEqual(failures, [])
        self.assertEqual(validate_fixtures(), [])

    def test_equivalent_prose_is_advisory(self) -> None:
        root = self.make_repository()
        skill = root / "phase-step-planner" / "SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8").replace(
            "Do not review every draft", "Review the finished handoff rather than each draft"),
            encoding="utf-8")
        failures, warnings = validate_declarations(root)
        self.assertEqual(failures, [])
        self.assertTrue(warnings)

    def test_reference_label_can_change(self) -> None:
        root = self.make_repository()
        skill = root / "deliver-code-change" / "SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8").replace(
            "[references/phase-handoff.md]", "[Phase execution contract]"), encoding="utf-8")
        failures, _ = validate_declarations(root)
        self.assertEqual(failures, [])

    def test_broken_reference_remains_an_error(self) -> None:
        root = self.make_repository()
        skill = root / "deliver-code-change" / "SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8").replace(
            "(references/phase-handoff.md)", "(references/missing.md)"), encoding="utf-8")
        failures, _ = validate_declarations(root)
        self.assertTrue(any("broken reference" in failure for failure in failures))

    def test_missing_resource_remains_an_error(self) -> None:
        root = self.make_repository()
        # Rename only this controlled fixture's resource to simulate its absence.
        path = root / "phase-step-planner" / "references" / "repair-loop.md"
        path.rename(path.with_suffix(".fixture"))
        failures, _ = validate_declarations(root)
        self.assertTrue(any("missing required resource" in failure for failure in failures))

    def test_invalid_template_structure_remains_an_error(self) -> None:
        root = self.make_repository()
        template = root / "phase-step-planner" / "assets" / "STEP_TEMPLATE.md"
        template.write_text(template.read_text(encoding="utf-8").replace(
            "## Acceptance", "## Different section"), encoding="utf-8")
        failures, _ = validate_declarations(root)
        self.assertTrue(any("STEP template" in failure for failure in failures))

    def test_unsupported_template_schemas_remain_errors(self) -> None:
        for name in ("STEP_TEMPLATE.md", "STATUS_TEMPLATE.md"):
            with self.subTest(name=name):
                root = self.make_repository()
                template = root / "phase-step-planner" / "assets" / name
                template.write_text(template.read_text(encoding="utf-8").replace(
                    "- Handoff schema: 1", "- Handoff schema: 99"), encoding="utf-8")
                failures, _ = validate_declarations(root)
                self.assertTrue(any("supported handoff schema" in failure for failure in failures))

    def test_invalid_index_table_remains_an_error(self) -> None:
        root = self.make_repository()
        template = root / "phase-step-planner" / "assets" / "PHASE_README_TEMPLATE.md"
        template.write_text(template.read_text(encoding="utf-8").replace(
            "| Step document |", "| Different column |"), encoding="utf-8")
        failures, _ = validate_declarations(root)
        self.assertTrue(any("five-column step table" in failure for failure in failures))


if __name__ == "__main__":
    unittest.main()
