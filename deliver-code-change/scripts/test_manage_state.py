from __future__ import annotations

import argparse
import json
import tempfile
import unittest
from pathlib import Path

from manage_state import initialize, load_state, update, validate_state, write_atomic


def init_args(path: Path) -> argparse.Namespace:
    return argparse.Namespace(
        file=str(path),
        task_id="task-1",
        route="Standard",
        step="inspect",
        resume_hint="",
    )


def update_args(path: Path) -> argparse.Namespace:
    return argparse.Namespace(
        file=str(path),
        step=None,
        complete=None,
        changed=None,
        verification=None,
        resume_hint=None,
    )


class ManageStateTests(unittest.TestCase):
    def make_path(self) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        return Path(temporary.name) / "state.json"

    def make_state(self, path: Path) -> dict[str, object]:
        return initialize(init_args(path))

    def write_unchecked(self, path: Path, state: dict[str, object]) -> None:
        path.write_text(json.dumps(state), encoding="utf-8")

    def test_valid_state_round_trip(self) -> None:
        path = self.make_path()
        state = self.make_state(path)
        write_atomic(path, state)
        self.assertEqual(load_state(path), state)

    def test_update_and_complete_produce_valid_states(self) -> None:
        path = self.make_path()
        write_atomic(path, self.make_state(path))
        args = update_args(path)
        args.step = "verify"
        args.complete = ["inspect", "implement"]
        args.changed = ["src/example.py"]
        args.verification = ["PASS: focused tests"]
        updated = update(args)
        write_atomic(path, updated)
        self.assertEqual(load_state(path)["current_step"], "verify")

        completed = update(update_args(path), complete_task=True)
        write_atomic(path, completed)
        self.assertEqual(load_state(path)["status"], "completed")

    def test_unknown_schema_version_is_rejected(self) -> None:
        path = self.make_path()
        state = self.make_state(path)
        state["schema_version"] = 99
        self.write_unchecked(path, state)
        with self.assertRaisesRegex(ValueError, "unsupported schema_version"):
            load_state(path)

    def test_non_object_state_is_rejected(self) -> None:
        path = self.make_path()
        path.write_text("[]", encoding="utf-8")
        with self.assertRaisesRegex(TypeError, "state must be a JSON object"):
            load_state(path)

    def test_missing_and_unknown_fields_are_rejected(self) -> None:
        state = self.make_state(self.make_path())
        del state["task_id"]
        state["unexpected"] = True
        with self.assertRaisesRegex(ValueError, "missing fields: task_id"):
            validate_state(state)
        with self.assertRaisesRegex(ValueError, "unknown fields: unexpected"):
            validate_state(state)

    def test_invalid_status_is_rejected_without_normalization(self) -> None:
        path = self.make_path()
        state = self.make_state(path)
        state["status"] = "mystery"
        self.write_unchecked(path, state)
        with self.assertRaisesRegex(ValueError, "invalid status"):
            load_state(path)

    def test_field_types_and_duplicate_lists_are_rejected(self) -> None:
        state = self.make_state(self.make_path())
        state["route"] = ["Standard"]
        state["changed_files"] = ["src/a.py", "src/a.py"]
        with self.assertRaisesRegex(ValueError, "invalid route"):
            validate_state(state)
        with self.assertRaisesRegex(ValueError, "must not contain duplicates"):
            validate_state(state)

    def test_completed_state_is_immutable(self) -> None:
        path = self.make_path()
        state = self.make_state(path)
        state["status"] = "completed"
        state["current_step"] = "complete"
        write_atomic(path, state)
        with self.assertRaisesRegex(ValueError, "completed state is immutable"):
            update(update_args(path))

    def test_completed_state_requires_terminal_step(self) -> None:
        state = self.make_state(self.make_path())
        state["status"] = "completed"
        with self.assertRaisesRegex(ValueError, "current_step `complete`"):
            validate_state(state)

    def test_timestamps_must_be_utc_and_monotonic(self) -> None:
        state = self.make_state(self.make_path())
        state["created_at"] = "2026-08-23T10:00:00+00:00"
        state["updated_at"] = "2026-08-23T09:00:00+00:00"
        with self.assertRaisesRegex(ValueError, "must not precede"):
            validate_state(state)
        state["updated_at"] = "2026-08-23T11:00:00+08:00"
        with self.assertRaisesRegex(ValueError, "must use UTC offset"):
            validate_state(state)


if __name__ == "__main__":
    unittest.main()
