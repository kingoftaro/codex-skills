from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock


MODULE_PATH = Path(__file__).with_name("detect_project.py")
SPEC = importlib.util.spec_from_file_location("detect_project_tests", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load project detector: {MODULE_PATH}")
DETECTOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DETECTOR)


class DetectProjectTests(unittest.TestCase):
    def test_common_python_environment_tools_are_discoverable(self) -> None:
        self.assertTrue({"uv", "poetry", "tox", "nox"}.issubset(DETECTOR.TOOL_NAMES))

    def test_current_interpreter_is_reported_when_python_is_not_on_path(self) -> None:
        with tempfile.TemporaryDirectory(prefix="detect-project-test-") as temporary:
            root = Path(temporary)
            interpreter = root / "python-runtime.exe"
            interpreter.write_bytes(b"")
            with (
                mock.patch.object(DETECTOR.shutil, "which", return_value=None),
                mock.patch.object(DETECTOR.sys, "executable", str(interpreter)),
            ):
                tools = DETECTOR.detect_tools()
            self.assertEqual(tools["python"], str(interpreter.resolve()))
            self.assertIsNone(tools["python3"])

    def test_python_sources_are_detected_without_a_manifest(self) -> None:
        with tempfile.TemporaryDirectory(prefix="detect-project-test-") as temporary:
            root = Path(temporary)
            (root / "example.py").write_text("value = 1\n", encoding="utf-8")
            result = DETECTOR.inspect(root)
            self.assertEqual(result["languages"], {"python": []})
            self.assertEqual(result["source_files"], {"total": 1, "by_suffix": {".py": 1}})


if __name__ == "__main__":
    unittest.main()
