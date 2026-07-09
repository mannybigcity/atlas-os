import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\PUTER")
HERMES_BRIDGE_PS1 = PROJECT_ROOT / "hermes_bridge.ps1"

BRAIN_DIR = PROJECT_ROOT / "RAMFAM_KINGDOM_BRAIN"
SKILLS_MD_DIR = BRAIN_DIR / "03_AGENT_SKILLS"
FOUNDRY_DIR = BRAIN_DIR / "04_MASON_FOUNDRY"
PY_SKILLS_DIR = PROJECT_ROOT / "skills"
TEMP_DIR = PROJECT_ROOT / "_mason_temp"

for folder in [SKILLS_MD_DIR, FOUNDRY_DIR, PY_SKILLS_DIR, TEMP_DIR]:
    folder.mkdir(parents=True, exist_ok=True)


def safe_name(agent):
    return agent.strip().lower().replace(" ", "_")


def ask_hermes_for_design(agent, skill_md):
    agent_safe = safe_name(agent)

    if not HERMES_BRIDGE_PS1.exists():
        return None

    prompt_file = TEMP_DIR / f"{agent_safe}_worker_request.md"
    prompt_file.write_text(f"""
MASON FOUNDRY SUBCONTRACTOR REQUEST

You are Hermes. You are the subcontractor.
Mason is the boss, editor, installer, and tester.

Design a Python worker for this RAMFAM KINGDOM agent.

AGENT: {agent}

SKILL FILE:
{skill_md}

Return ONLY Python code.
No markdown fences.
No explanation.

Required:
- Function name: {agent_safe}_agent(task)
- Accept task as string
- Return a dictionary
- Include these keys:
  agent
  status
  task
  summary
  recommendation
  approval_required
  timestamp
- Manny approval required for public, financial, customer-facing, or reputation-impacting actions
- No external APIs
- No file deletion
- Safe Windows Python
""", encoding="utf-8")

    tiny_prompt = f"Read this request file and return only Python code: {prompt_file}"

    try:
        result = subprocess.run(
            [
                "powershell",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(HERMES_BRIDGE_PS1),
                "-Prompt",
                tiny_prompt
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60
        )

        if result.returncode == 0 and "def " in result.stdout:
            return result.stdout.strip()

    except subprocess.TimeoutExpired:
        return None
    except Exception:
        return None

    return None


def mason_fallback_worker(agent):
    agent_safe = safe_name(agent)
    fn = f"{agent_safe}_agent"

    return f'''from datetime import datetime

def {fn}(task):
    task_text = str(task).strip()

    if not task_text:
        return {{
            "agent": "{agent}",
            "status": "error",
            "task": "",
            "summary": "No task was provided.",
            "recommendation": "Provide a clear task for {agent}.",
            "approval_required": False,
            "timestamp": datetime.now().isoformat()
        }}

    approval_words = [
        "send", "post", "publish", "invoice", "quote", "customer",
        "client", "public", "pay", "price", "legal", "contract",
        "facebook", "instagram", "tiktok", "website", "email", "dm",
        "order", "cost", "revenue", "profit", "hat", "shirt",
        "sell", "sale", "money", "payment", "vendor", "supplier"
    ]

    approval_required = any(word in task_text.lower() for word in approval_words)

    return {{
        "agent": "{agent}",
        "status": "success",
        "task": task_text,
        "summary": "{agent} reviewed the task using the assigned RAMFAM KINGDOM skill file.",
        "recommendation": "Prepare the next practical action. Stop for Manny approval if this affects customers, money, public posts, or reputation.",
        "approval_required": approval_required,
        "timestamp": datetime.now().isoformat()
    }}

if __name__ == "__main__":
    print({fn}("Evaluate a 50 hat order at $19 each with $12 hat cost and $0.75 patch cost."))
'''


def clean_code(code):
    if not code:
        return code

    code = code.replace("```python", "")
    code = code.replace("```", "")
    code = code.strip()

    if "from datetime import datetime" not in code:
        code = "from datetime import datetime\n\n" + code

    return code


def enforce_test_block(agent, code):
    agent_safe = safe_name(agent)
    fn = f"{agent_safe}_agent"

    test_block = f'''

if __name__ == "__main__":
    print({fn}("Evaluate a 50 hat order at $19 each with $12 hat cost and $0.75 patch cost."))
'''

    if 'if __name__ == "__main__"' not in code:
        code = code.rstrip() + test_block

    return code


def test_worker(worker_file):
    try:
        result = subprocess.run(
            [sys.executable, str(worker_file)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=20
        )

        return {
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip()
        }

    except subprocess.TimeoutExpired:
        return {
            "returncode": 999,
            "stdout": "",
            "stderr": "Worker test timed out."
        }


def build_agent(agent):
    agent = agent.strip().title()
    agent_upper = agent.upper()
    agent_safe = safe_name(agent)

    skill_file = SKILLS_MD_DIR / f"{agent_upper}_SKILLS.md"
    worker_file = PY_SKILLS_DIR / f"{agent_safe}_agent.py"

    if not skill_file.exists():
        print(f"ERROR: Missing skill file: {skill_file}")
        return

    skill_md = skill_file.read_text(encoding="utf-8", errors="replace")

    print(f"Mason reading skill file: {skill_file}")
    print("Mason asking Hermes subcontractor through PowerShell bridge...")

    hermes_code = ask_hermes_for_design(agent, skill_md)

    if hermes_code:
        print("Hermes returned worker design through bridge.")
        source = "Hermes through PowerShell bridge"
        code = clean_code(hermes_code)
    else:
        print("Hermes bridge failed or timed out. Mason using fallback builder.")
        source = "Mason fallback"
        code = mason_fallback_worker(agent)

    code = enforce_test_block(agent, code)

    worker_file.write_text(code, encoding="utf-8")

    print(f"Mason installed worker: {worker_file}")
    print("Mason testing worker...")

    test_result = test_worker(worker_file)

    if test_result["returncode"] != 0 or not test_result["stdout"]:
        print("Worker failed test or returned blank output. Mason replacing with fallback worker.")
        source = "Mason fallback after failed Hermes test"
        code = mason_fallback_worker(agent)
        worker_file.write_text(code, encoding="utf-8")
        test_result = test_worker(worker_file)

    report = {
        "agent": agent,
        "source": source,
        "bridge_file": str(HERMES_BRIDGE_PS1),
        "worker_file": str(worker_file),
        "skill_file": str(skill_file),
        "test_result": test_result,
        "timestamp": datetime.now().isoformat()
    }

    report_file = FOUNDRY_DIR / f"{agent_upper}_BUILD_REPORT.json"
    report_file.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("Mason build complete.")
    print(f"Report: {report_file}")
    print("Test output:")
    print(test_result["stdout"])

    if test_result["stderr"]:
        print("Errors:")
        print(test_result["stderr"])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python mason_foundry_builder.py Hunter")
    else:
        build_agent(sys.argv[1])