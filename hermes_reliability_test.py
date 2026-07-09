import subprocess
import time
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\PUTER")
HERMES_EXE = Path(r"C:\Users\User\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes.exe")
TEMP_DIR = PROJECT_ROOT / "_mason_temp"
REPORT_FILE = PROJECT_ROOT / "RAMFAM_KINGDOM_BRAIN" / "04_MASON_FOUNDRY" / "HERMES_RELIABILITY_TEST.md"

TEMP_DIR.mkdir(parents=True, exist_ok=True)
REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

TESTS = [
    {
        "name": "Tiny direct prompt",
        "mode": "direct",
        "prompt": "Return only this exact text: HERMES_OK"
    },
    {
        "name": "Tiny file prompt",
        "mode": "file",
        "content": "Return only this exact text: HERMES_FILE_OK"
    },
    {
        "name": "Small code prompt",
        "mode": "file",
        "content": """
Return only Python code. No markdown.

Create a function named test_agent(task) that returns a dictionary with:
agent, status, task, summary, recommendation, approval_required, timestamp.
"""
    }
]

def run_hermes(prompt, timeout_seconds):
    start = time.time()

    try:
        result = subprocess.run(
            [str(HERMES_EXE), "-z", prompt],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds
        )

        elapsed = round(time.time() - start, 2)

        return {
            "ok": result.returncode == 0,
            "returncode": result.returncode,
            "seconds": elapsed,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "timed_out": False
        }

    except subprocess.TimeoutExpired:
        elapsed = round(time.time() - start, 2)

        return {
            "ok": False,
            "returncode": 999,
            "seconds": elapsed,
            "stdout": "",
            "stderr": f"Timed out after {timeout_seconds} seconds.",
            "timed_out": True
        }

def main():
    lines = [
        "# Hermes Reliability Test",
        f"Generated: {datetime.now().isoformat()}",
        "",
        f"Hermes EXE: `{HERMES_EXE}`",
        "",
    ]

    print("HERMES RELIABILITY TEST STARTING")
    print("=" * 60)

    for test in TESTS:
        print(f"Running: {test['name']}")

        if test["mode"] == "direct":
            prompt = test["prompt"]
        else:
            prompt_file = TEMP_DIR / f"{test['name'].lower().replace(' ', '_')}.md"
            prompt_file.write_text(test["content"], encoding="utf-8")
            prompt = f"Read this file and follow the instructions exactly: {prompt_file}"

        result = run_hermes(prompt, timeout_seconds=20)

        print(f"Seconds: {result['seconds']}")
        print(f"OK: {result['ok']}")
        print(f"Timed out: {result['timed_out']}")
        print("-" * 60)

        lines.extend([
            f"## {test['name']}",
            f"- OK: {result['ok']}",
            f"- Timed out: {result['timed_out']}",
            f"- Seconds: {result['seconds']}",
            f"- Return code: {result['returncode']}",
            "",
            "### STDOUT",
            "```",
            result["stdout"],
            "```",
            "",
            "### STDERR",
            "```",
            result["stderr"],
            "```",
            "",
        ])

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")

    print("HERMES RELIABILITY TEST COMPLETE")
    print(f"Report saved to: {REPORT_FILE}")

if __name__ == "__main__":
    main()