from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VERIFIER = ROOT / "mason_verifier.py"


def run_verifier(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VERIFIER), *args],
        cwd=str(cwd or ROOT),
        text=True,
        capture_output=True,
    )


def parse_stdout_json(result: subprocess.CompletedProcess[str]) -> dict[str, object]:
    assert result.stdout.strip(), result.stderr
    return json.loads(result.stdout)


class MasonVerifierTests(unittest.TestCase):
    def test_mason_verifier_imports_without_side_effects(self) -> None:
        spec = importlib.util.spec_from_file_location("mason_verifier", VERIFIER)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)  # type: ignore[union-attr]
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[union-attr]
        self.assertTrue(callable(module.verify_python_file))

    def test_passes_when_file_exists_runs_imports_and_outputs_expected_text(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            target = temp_path / "sample_target.py"
            target.write_text(
                "MESSAGE = 'Mason verifier target ready'\n"
                "def main():\n"
                "    print(MESSAGE)\n"
                "if __name__ == '__main__':\n"
                "    main()\n",
                encoding="utf-8",
            )

            result = run_verifier(
                str(target),
                "Mason verifier target ready",
                "--report-dir",
                str(temp_path / "reports"),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = parse_stdout_json(result)
            self.assertEqual(payload["status"], "PASS")
            checks = payload["checks"]
            self.assertTrue(checks["file_exists"]["passed"])
            self.assertTrue(checks["run_python_file"]["passed"])
            self.assertTrue(checks["expected_output_text"]["passed"])
            self.assertTrue(checks["import_works"]["passed"])
            report_path = Path(str(payload["report_path"]))
            self.assertTrue(report_path.exists())
            report = report_path.read_text(encoding="utf-8")
            self.assertIn("# Mason Verifier Report", report)
            self.assertIn("Overall status: PASS", report)

    def test_fails_when_expected_output_is_missing_but_still_generates_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            target = temp_path / "quiet_target.py"
            target.write_text("print('different text')\n", encoding="utf-8")

            result = run_verifier(
                str(target),
                "required text",
                "--report-dir",
                str(temp_path / "reports"),
            )

            self.assertEqual(result.returncode, 1)
            payload = parse_stdout_json(result)
            self.assertEqual(payload["status"], "FAIL")
            self.assertTrue(payload["checks"]["file_exists"]["passed"])
            self.assertTrue(payload["checks"]["run_python_file"]["passed"])
            self.assertFalse(payload["checks"]["expected_output_text"]["passed"])
            self.assertTrue(Path(str(payload["report_path"])).exists())

    def test_fails_cleanly_when_file_does_not_exist_and_generates_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            missing = temp_path / "missing.py"

            result = run_verifier(
                str(missing),
                "anything",
                "--report-dir",
                str(temp_path / "reports"),
            )

            self.assertEqual(result.returncode, 1)
            payload = parse_stdout_json(result)
            self.assertEqual(payload["status"], "FAIL")
            self.assertFalse(payload["checks"]["file_exists"]["passed"])
            self.assertFalse(payload["checks"]["run_python_file"]["passed"])
            self.assertFalse(payload["checks"]["import_works"]["passed"])
            self.assertTrue(Path(str(payload["report_path"])).exists())


if __name__ == "__main__":
    unittest.main()
