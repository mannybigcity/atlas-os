from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RETRY_ENGINE = ROOT / "skills" / "mason_retry_engine.py"


def load_retry_engine():
    spec = importlib.util.spec_from_file_location("mason_retry_engine", RETRY_ENGINE)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MasonRetryEngineTests(unittest.TestCase):
    def test_import_exposes_mason_retry_python(self) -> None:
        module = load_retry_engine()
        self.assertTrue(callable(module.mason_retry_python))

    def test_passing_file_succeeds_on_first_attempt_and_writes_report(self) -> None:
        module = load_retry_engine()
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "passing_target.py"
            target.write_text(
                "MESSAGE = 'retry engine pass target'\n"
                "def main():\n"
                "    print(MESSAGE)\n"
                "if __name__ == '__main__':\n"
                "    main()\n",
                encoding="utf-8",
            )

            result = module.mason_retry_python(str(target), "retry engine pass target", max_attempts=3)

        self.assertEqual(result["status"], "success", json.dumps(result, indent=2))
        self.assertEqual(result["attempt_count"], 1)
        self.assertEqual(len(result["attempts"]), 1)
        self.assertEqual(result["attempts"][0]["status"], "PASS")
        self.assertIn("stdout", result["attempts"][0])
        self.assertIn("stderr", result["attempts"][0])
        self.assertTrue(Path(result["report_path"]).exists())
        report_text = Path(result["report_path"]).read_text(encoding="utf-8")
        self.assertIn("# Mason Retry Engine Report", report_text)
        self.assertIn("Final status: success", report_text)
        self.assertTrue(result["memory_entry"])

    def test_failing_file_retries_max_attempts_and_returns_details(self) -> None:
        module = load_retry_engine()
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "failing_target.py"
            target.write_text(
                "import sys\n"
                "print('failure stdout marker')\n"
                "print('failure stderr marker', file=sys.stderr)\n"
                "raise SystemExit(7)\n",
                encoding="utf-8",
            )

            result = module.mason_retry_python(str(target), "required missing text", max_attempts=2)

        self.assertEqual(result["status"], "failed", json.dumps(result, indent=2))
        self.assertEqual(result["attempt_count"], 2)
        self.assertEqual(len(result["attempts"]), 2)
        self.assertTrue(all(attempt["status"] == "FAIL" for attempt in result["attempts"]))
        self.assertIn("failure stdout marker", result["stdout"])
        self.assertIn("failure stderr marker", result["stderr"])
        self.assertTrue(result["error"])
        self.assertTrue(Path(result["report_path"]).exists())
        self.assertTrue(result["memory_entry"])

    def test_expected_text_defaults_to_empty_string_so_runnable_importable_file_can_pass(self) -> None:
        module = load_retry_engine()
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "default_expected_text_target.py"
            target.write_text("VALUE = 42\n", encoding="utf-8")
            result = module.mason_retry_python(str(target), max_attempts=1)

        self.assertEqual(result["status"], "success", json.dumps(result, indent=2))
        self.assertEqual(result["expected_text"], "")


if __name__ == "__main__":
    unittest.main()
