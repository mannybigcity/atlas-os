import subprocess
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\PUTER")
HERMES_EXE = Path(r"C:\Users\User\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes.exe")

TASKS = [
    "Return ONLY this text: FUNCTION_OK",
    "Return ONLY this text: APPROVAL_OK",
    "Return ONLY this text: RECOMMENDATION_OK",
    "Return ONLY this text: TESTBLOCK_OK"
]

def ask_hermes(prompt):
    try:
        result = subprocess.run(
            [
                str(HERMES_EXE),
                "-z",
                prompt,
                "--ignore-rules",
                "--ignore-user-config"
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15
        )

        return {
            "success": result.returncode == 0,
            "output": result.stdout.strip(),
            "error": result.stderr.strip()
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "",
            "error": "TIMEOUT"
        }


def main():
    print("=" * 60)
    print("MASON MICROTASK ENGINE TEST")
    print("=" * 60)

    successful_jobs = 0
    outputs = []

    for index, task in enumerate(TASKS, start=1):

        print(f"\nRunning Job {index}")

        result = ask_hermes(task)

        if result["success"]:
            print(f"Job {index} SUCCESS")
            print(result["output"])
            successful_jobs += 1
            outputs.append(result["output"])

        else:
            print(f"Job {index} FAILED")
            print(result["error"])

    print("\n" + "=" * 60)

    if successful_jobs == len(TASKS):
        print("ALL MICROTASKS SUCCEEDED")

        print("\nAssembly Result:")

        assembled_worker = {
            "function": outputs[0],
            "approval": outputs[1],
            "recommendation": outputs[2],
            "test_block": outputs[3]
        }

        print(assembled_worker)

    else:
        print("MICROTASK ENGINE FAILED")

    print("=" * 60)
    print(f"Completed: {datetime.now()}")


if __name__ == "__main__":
    main()