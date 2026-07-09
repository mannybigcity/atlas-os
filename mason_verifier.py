from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

DEFAULT_REPORT_DIR = Path("mason_workspace") / "reports"


def _check(name: str, passed: bool, details: str = "", **extra: Any) -> dict[str, Any]:
    check: dict[str, Any] = {
        "name": name,
        "passed": bool(passed),
        "details": details,
    }
    check.update(extra)
    return check


def _now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _run_python_file(target_path: Path, timeout: int) -> subprocess.CompletedProcess[str] | None:
    if not target_path.exists():
        return None
    return subprocess.run(
        [sys.executable, str(target_path)],
        cwd=str(target_path.parent),
        text=True,
        capture_output=True,
        timeout=timeout,
    )


def _verify_import(target_path: Path, timeout: int) -> subprocess.CompletedProcess[str] | None:
    if not target_path.exists():
        return None

    import_code = (
        "import importlib.util, pathlib, sys; "
        f"path = pathlib.Path({str(target_path)!r}); "
        "sys.path.insert(0, str(path.parent)); "
        "spec = importlib.util.spec_from_file_location(path.stem, path); "
        "assert spec is not None and spec.loader is not None, 'could not create import spec'; "
        "module = importlib.util.module_from_spec(spec); "
        "sys.modules[path.stem] = module; "
        "spec.loader.exec_module(module); "
        "print('IMPORT_OK')"
    )
    return subprocess.run(
        [sys.executable, "-c", import_code],
        cwd=str(target_path.parent),
        text=True,
        capture_output=True,
        timeout=timeout,
    )


def _write_report(result: dict[str, Any], report_dir: Path) -> Path:
    report_dir.mkdir(parents=True, exist_ok=True)
    target_stem = Path(str(result["target_path"])).stem or "missing_target"
    report_path = report_dir / f"mason_verifier_report_{target_stem}_{_now_stamp()}.md"

    checks: dict[str, dict[str, Any]] = result["checks"]
    lines = [
        "# Mason Verifier Report",
        "",
        f"Generated: {result['generated_at']}",
        f"Target file: `{result['target_path']}`",
        f"Expected output text: `{result['expected_output_text']}`",
        f"Overall status: {result['status']}",
        "",
        "## Checks",
    ]

    for key in ("file_exists", "run_python_file", "expected_output_text", "import_works"):
        check = checks[key]
        marker = "PASS" if check["passed"] else "FAIL"
        lines.extend(
            [
                f"- {marker} `{key}`: {check.get('details', '')}",
            ]
        )

    lines.extend(
        [
            "",
            "## Run Output",
            "",
            "### stdout",
            "```",
            str(result.get("stdout", "")),
            "```",
            "",
            "### stderr",
            "```",
            str(result.get("stderr", "")),
            "```",
            "",
            "## Import Output",
            "",
            "### stdout",
            "```",
            str(result.get("import_stdout", "")),
            "```",
            "",
            "### stderr",
            "```",
            str(result.get("import_stderr", "")),
            "```",
            "",
        ]
    )

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def verify_python_file(
    target_file: str | Path,
    expected_output_text: str,
    report_dir: str | Path = DEFAULT_REPORT_DIR,
    timeout: int = 30,
) -> dict[str, Any]:
    """Verify a Python file exists, runs, outputs expected text, imports, and report results."""

    target_path = Path(target_file).expanduser().resolve()
    report_dir_path = Path(report_dir).expanduser().resolve()
    generated_at = datetime.now().isoformat(timespec="seconds")

    file_exists = target_path.exists() and target_path.is_file()
    checks: dict[str, dict[str, Any]] = {
        "file_exists": _check(
            "file_exists",
            file_exists,
            "File exists." if file_exists else "File does not exist.",
        )
    }

    stdout = ""
    stderr = ""
    return_code: int | None = None

    try:
        run_result = _run_python_file(target_path, timeout)
        if run_result is None:
            checks["run_python_file"] = _check(
                "run_python_file",
                False,
                "Skipped because target file does not exist.",
            )
        else:
            stdout = run_result.stdout
            stderr = run_result.stderr
            return_code = run_result.returncode
            checks["run_python_file"] = _check(
                "run_python_file",
                run_result.returncode == 0,
                f"Python process exited with code {run_result.returncode}.",
                return_code=run_result.returncode,
            )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        checks["run_python_file"] = _check(
            "run_python_file",
            False,
            f"Python process timed out after {timeout} seconds.",
        )

    combined_output = f"{stdout}\n{stderr}"
    output_matches = expected_output_text in combined_output if file_exists else False
    checks["expected_output_text"] = _check(
        "expected_output_text",
        output_matches,
        "Expected text found in process output."
        if output_matches
        else "Expected text was not found in process output.",
    )

    import_stdout = ""
    import_stderr = ""
    import_return_code: int | None = None

    try:
        import_result = _verify_import(target_path, timeout)
        if import_result is None:
            checks["import_works"] = _check(
                "import_works",
                False,
                "Skipped because target file does not exist.",
            )
        else:
            import_stdout = import_result.stdout
            import_stderr = import_result.stderr
            import_return_code = import_result.returncode
            checks["import_works"] = _check(
                "import_works",
                import_result.returncode == 0 and "IMPORT_OK" in import_result.stdout,
                f"Import process exited with code {import_result.returncode}.",
                return_code=import_result.returncode,
            )
    except subprocess.TimeoutExpired as exc:
        import_stdout = exc.stdout or ""
        import_stderr = exc.stderr or ""
        checks["import_works"] = _check(
            "import_works",
            False,
            f"Import process timed out after {timeout} seconds.",
        )

    status = "PASS" if all(check["passed"] for check in checks.values()) else "FAIL"
    result: dict[str, Any] = {
        "status": status,
        "generated_at": generated_at,
        "target_path": str(target_path),
        "expected_output_text": expected_output_text,
        "checks": checks,
        "return_code": return_code,
        "stdout": stdout,
        "stderr": stderr,
        "import_return_code": import_return_code,
        "import_stdout": import_stdout,
        "import_stderr": import_stderr,
    }

    report_path = _write_report(result, report_dir_path)
    result["report_path"] = str(report_path)
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Mason verifier: file existence, execution, expected output, import, and report."
    )
    parser.add_argument("target_file", help="Python file to verify.")
    parser.add_argument("expected_output_text", help="Text expected in stdout/stderr when the file runs.")
    parser.add_argument(
        "--report-dir",
        default=str(DEFAULT_REPORT_DIR),
        help="Directory where the markdown report is written. Default: mason_workspace/reports",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Timeout in seconds for run and import checks. Default: 30",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = verify_python_file(
        target_file=args.target_file,
        expected_output_text=args.expected_output_text,
        report_dir=args.report_dir,
        timeout=args.timeout,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
