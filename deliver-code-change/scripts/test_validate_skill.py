from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from validate_skill import validate

VALID_SKILL = """---
name: demo-skill
description: Perform one demonstrative task when explicitly relevant.
---

# Demo

Follow the requested boundary.
"""

VALID_AGENT = """interface:
  display_name: "Demo Skill"
  short_description: "Perform one demonstrative task"
  default_prompt: "Use $demo-skill for this task."
"""


class ValidateSkillTests(unittest.TestCase):
    def make_skill(
        self,
        *,
        skill_text: str = VALID_SKILL,
        agent_text: str = VALID_AGENT,
    ) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name) / "demo-skill"
        root.joinpath("agents").mkdir(parents=True)
        root.joinpath("SKILL.md").write_text(skill_text, encoding="utf-8")
        root.joinpath("agents", "openai.yaml").write_text(agent_text, encoding="utf-8")
        return root

    def test_valid_skill_passes(self) -> None:
        self.assertEqual(validate(self.make_skill()), [])

    def test_duplicate_frontmatter_key_fails(self) -> None:
        skill = VALID_SKILL.replace(
            "description: Perform one demonstrative task when explicitly relevant.",
            "description: Perform one demonstrative task when explicitly relevant.\n"
            "description: Duplicate description.",
        )
        errors = validate(self.make_skill(skill_text=skill))
        self.assertIn("duplicate frontmatter key: description", errors)

    def test_interface_fields_must_be_nested(self) -> None:
        agent = VALID_AGENT.replace("  display_name:", "display_name:")
        errors = validate(self.make_skill(agent_text=agent))
        self.assertIn("agents/openai.yaml missing interface.display_name", errors)

    def test_duplicate_interface_field_fails(self) -> None:
        agent = VALID_AGENT + '  default_prompt: "Use $demo-skill again."\n'
        errors = validate(self.make_skill(agent_text=agent))
        self.assertIn("duplicate interface field: default_prompt", errors)


if __name__ == "__main__":
    unittest.main()
