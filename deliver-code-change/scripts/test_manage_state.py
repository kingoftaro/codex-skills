from __future__ import annotations

import argparse
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("manage_state.py")
SPEC = importlib.util.spec_from_file_location("manage_state_tests", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load state manager: {MODULE_PATH}")
MANAGER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MANAGER)


def initialize_args(path: Path) -> argparse.Namespace:
    return argparse.Namespace(
        file=str(path),
        task_id="example-task",
        route="Standard",
        step="inspect",
        resume_hint="",
    )


def update_args(path: Path, *, step: str | None = None) -> argparse.Namespace:
    return argparse.Namespace(
        file=str(path),
        step=step,
        complete=None,
        changed=None,
        verification=None,
        resume_hint=None,
    )


class ManageStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="manage-state-test-")
        self.path = Path(self.temporary.name) / "state.json"
        self.state = MANAGER.initialize(initialize_args(self.path))
        MANAGER.write_atomic(self.path, self.state)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_valid_state_round_trip(self) -> None:
        self.assertEqual(MANAGER.load_state(self.path), self.state)

    def test_completed_state_is_immutable(self) -> None:
        completed = MANAGER.update(update_args(self.path), complete_task=True)
        MANAGER.write_atomic(self.path, completed)
        with self.assertRaisesRegex(ValueError, "completed state is immutable"):
            MANAGER.update(update_args(self.path, step="reopened"))

    def test_contradictory_completed_state_is_rejected(self) -> None:
        invalid = dict(self.state, status="completed", current_step="reopened")
        self.path.write_text(json.dumps(invalid), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "completed state must use current_step 'complete'"):
            MANAGER.load_state(self.path)

    def test_non_list_history_is_rejected(self) -> None:
        invalid = dict(self.state, changed_files="src/example.py")
        self.path.write_text(json.dumps(invalid), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "changed_files must be an array of strings"):
            MANAGER.load_state(self.path)

    def test_boolean_schema_version_is_rejected(self) -> None:
        invalid = dict(self.state, schema_version=True)
        self.path.write_text(json.dumps(invalid), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "unsupported state schema_version"):
            MANAGER.load_state(self.path)

    def test_timestamps_require_timezones(self) -> None:
        invalid = dict(self.state, updated_at="2026-08-14T10:00:00")
        self.path.write_text(json.dumps(invalid), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "updated_at must include a timezone"):
            MANAGER.load_state(self.path)


if __name__ == "__main__":
    unittest.main()
