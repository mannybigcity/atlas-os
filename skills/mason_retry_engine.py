"""Mason retry engine for verifier-backed Python file checks.

Atlas can call mason_retry_python() when Mason needs to repeatedly verify a
Python artifact, preserve every attempt, write a report trail, and store the
final result in Mason memory.
"""

from __future__ import annotations

import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\PUTER")
SKILLS_DIR = PROJECT_ROOT / "skills"
MASON_WORKSPACE = PROJECT_ROOT / "mason_workspace"
REPORTS_DIR = MASON_WORKSPACE / "reports"

for import_path in (PROJECT_ROOT, SKILLS_DIR):
    import_path_text = str(import_path)
    if import_path_text not in sys.path:
        sys.path.insert(0, import_path_text)

from mason_memory import mason_remember  # noqa: E402
from mason_verifier import verify_python_file  # noqa: E402


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _slug(value: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "_" for ch in value).strip("_")
    while "__" in cleaned:
        cleaned = cleaned.replace("__", "_")
    return cleaned[:80] or "python_file"


def _normalize_max_attempts(max_attempts: int) -> int:
    try:
        attempts = int(max_attempts)
    except (TypeError, ValueError) as exc:
        raise ValueError("max_attempts must be an integer >= 1") from exc
    if attempts < 1:
        raise ValueError("max_attempts must be >= 1")
    return attempts


def _attempt_from_verifier(attempt_number: int, verifier_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "attempt": attempt_number,
        "status": verifier_result.get("status", "FAIL"),
        "passed": verifier_result.get("status") == "PASS",
        "generated_at": verifier_result.get("generated_at"),
        "return_code": verifier_result.get("return_code"),
        "stdout": verifier_result.get("stdout", ""),
        "stderr": verifier_result.get("stderr", ""),
        "import_return_code": verifier_result.get("import_return_code"),
        "import_stdout": verifier_result.get("import_stdout", ""),
        "import_stderr": verifier_result.get("import_stderr", ""),
        "checks": verifier_result.get("checks", {}),
        "verifier_report_path": verifier_result.get("report_path"),
        "error": "" if verifier_result.get("status") == "PASS" else _summarize_failure(verifier_result),
    }


def _summarize_failure(verifier_result: dict[str, Any]) -> str:
    checks = verifier_result.get("checks", {})
    failed_checks: list[str] = []
    if isinstance(checks, dict):
        for check_name, check in checks.items():
            if isinstance(check, dict) and not check.get("passed"):
                details = check.get("details", "")
                failed_checks.append(f"{check_name}: {details}".strip())
    if failed_checks:
        return "; ".join(failed_checks)
    stderr = str(verifier_result.get("stderr") or verifier_result.get("import_stderr") or "").strip()
    if stderr:
        return stderr
    return "Mason verifier returned FAIL."


def _write_retry_report(result: dict[str, Any]) -> str:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    target_stem = _slug(Path(str(result["file_path"])).stem)
    report_path = REPORTS_DIR / f"mason_retry_engine_{target_stem}_{_stamp()}.md"

    lines = [
        "# Mason Retry Engine Report",
        "",
        f"Generated: {result['generated_at']}",
        f"Target file: `{result['file_path']}`",
        f"Expected text: `{result['expected_text']}`",
        f"Max attempts: {result['max_attempts']}",
        f"Attempt count: {result['attempt_count']}",
        f"Final status: {result['status']}",
        f"Error: {result.get('error', '')}",
        "",
        "## Attempts",
    ]

    for attempt in result["attempts"]:
        lines.extend(
            [
                "",
                f"### Attempt {attempt['attempt']}: {attempt['status']}",
                f"Verifier report: `{attempt.get('verifier_report_path')}`",
                f"Return code: {attempt.get('return_code')}",
                f"Import return code: {attempt.get('import_return_code')}",
                f"Error: {attempt.get('error', '')}",
                "",
                "#### stdout",
                "```",
                str(attempt.get("stdout", "")),
                "```",
                "",
                "#### stderr",
                "```",
                str(attempt.get("stderr", "")),
                "```",
                "",
                "#### import stdout",
                "```",
                str(attempt.get("import_stdout", "")),
                "```",
                "",
                "#### import stderr",
                "```",
                str(attempt.get("import_stderr", "")),
                "```",
                "",
                "#### checks",
                "```json",
                json.dumps(attempt.get("checks", {}), indent=2, ensure_ascii=False),
                "```",
            ]
        )

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(report_path)


def mason_retry_python(file_path: str | Path, expected_text: str | None = None, max_attempts: int = 3) -> dict[str, Any]:
    """Run mason_verifier.py against a Python file until it passes or attempts run out.

    Args:
        file_path: Python file to verify.
        expected_text: Text expected in stdout/stderr. None means an empty
            string, allowing runnable/importable files with no output to pass.
        max_attempts: Maximum verifier attempts before returning failed.

    Returns:
        A JSON-serializable result dict with status, attempts, stdout/stderr,
        report_path, and Mason memory metadata.
    """

    attempts_limit = _normalize_max_attempts(max_attempts)
    target_path = Path(file_path).expanduser().resolve()
    expected = "" if expected_text is None else str(expected_text)
    attempts: list[dict[str, Any]] = []

    final_status = "failed"
    final_error = "Verification did not run."
    final_stdout = ""
    final_stderr = ""

    for attempt_number in range(1, attempts_limit + 1):
        try:
            verifier_result = verify_python_file(
                target_file=target_path,
                expected_output_text=expected,
                report_dir=REPORTS_DIR,
            )
            attempt = _attempt_from_verifier(attempt_number, verifier_result)
        except Exception as exc:  # defensive: return details instead of hiding verifier errors
            attempt = {
                "attempt": attempt_number,
                "status": "FAIL",
                "passed": False,
                "generated_at": _utc_now(),
                "return_code": None,
                "stdout": "",
                "stderr": "",
                "import_return_code": None,
                "import_stdout": "",
                "import_stderr": "",
                "checks": {},
                "verifier_report_path": None,
                "error": f"{exc.__class__.__name__}: {exc}",
                "traceback": traceback.format_exc(),
            }

        attempts.append(attempt)
        final_stdout = str(attempt.get("stdout", ""))
        final_stderr = str(attempt.get("stderr", ""))
        final_error = str(attempt.get("error", ""))

        if attempt.get("passed"):
            final_status = "success"
            final_error = ""
            break

    result: dict[str, Any] = {
        "status": final_status,
        "file_path": str(target_path),
        "expected_text": expected,
        "max_attempts": attempts_limit,
        "attempt_count": len(attempts),
        "generated_at": _utc_now(),
        "attempts": attempts,
        "stdout": final_stdout,
        "stderr": final_stderr,
        "error": final_error,
    }
    result["report_path"] = _write_retry_report(result)

    memory_payload = {
        "type": "mason_retry_python_result",
        "status": result["status"],
        "file_path": result["file_path"],
        "expected_text": result["expected_text"],
        "max_attempts": result["max_attempts"],
        "attempt_count": result["attempt_count"],
        "report_path": result["report_path"],
        "error": result["error"],
    }
    result["memory_entry"] = mason_remember(memory_payload)
    return result


__all__ = [
    "mason_retry_python",
    "PROJECT_ROOT",
    "MASON_WORKSPACE",
    "REPORTS_DIR",
]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Mason retry engine for Python verification.")
    parser.add_argument("file_path")
    parser.add_argument("expected_text", nargs="?", default=None)
    parser.add_argument("--max-attempts", type=int, default=3)
    args = parser.parse_args()
    print(
        json.dumps(
            mason_retry_python(args.file_path, args.expected_text, args.max_attempts),
            indent=2,
            ensure_ascii=False,
        )
    )
