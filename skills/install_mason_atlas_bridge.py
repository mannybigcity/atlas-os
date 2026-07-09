from pathlib import Path
import json

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\PUTER")
SKILLS_DIR = PROJECT_ROOT / "skills"
AGENTS_DIR = PROJECT_ROOT / "agents"
WORKSPACE = PROJECT_ROOT / "mason_workspace"

SKILLS_DIR.mkdir(parents=True, exist_ok=True)
AGENTS_DIR.mkdir(parents=True, exist_ok=True)
WORKSPACE.mkdir(parents=True, exist_ok=True)

mason_agent_code = r'''from pathlib import Path
import sys
import json
from datetime import datetime

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\PUTER")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

WORKSPACE = PROJECT_ROOT / "mason_workspace"
QUEUE_FILE = WORKSPACE / "mason_task_queue.json"
REPORTS_DIR = WORKSPACE / "reports"

WORKSPACE.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def now():
    return datetime.now().isoformat(timespec="seconds")


def load_queue():
    if not QUEUE_FILE.exists():
        QUEUE_FILE.write_text("[]", encoding="utf-8")
    return json.loads(QUEUE_FILE.read_text(encoding="utf-8-sig"))


def save_queue(tasks):
    QUEUE_FILE.write_text(json.dumps(tasks, indent=2), encoding="utf-8")


def detect_task_type(task):
    text = (task or "").lower()

    if "verify" in text or "test all" in text or "check all" in text:
        return "run_python", str(PROJECT_ROOT / "agents" / "test_all_agent_delegation.py")

    if "strengthen" in text or "upgrade kingdom" in text or "strengthen atlas" in text:
        return "run_python", str(PROJECT_ROOT / "skills" / "mason_kingdom_strengthener.py")

    if "inspect" in text or "look at" in text or "read file" in text:
        return "inspect_file", None

    if "run" in text and ".py" in text:
        return "run_python", None

    if "delegation" in text or "atlas" in text:
        return "build_agent_delegation", None

    return "auto_builder", None


def extract_file_path(task):
    text = task or ""
    marker = "C:\\"
    if marker not in text:
        return None

    start = text.find(marker)
    possible = text[start:].strip().strip('"').strip("'")
    return possible


def create_mason_task(task, context=None):
    context = context or {}
    tasks = load_queue()

    task_type, default_file = detect_task_type(task)
    file_path = context.get("file") or extract_file_path(task) or default_file

    new_task = {
        "id": f"atlas_mason_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "status": "pending",
        "agent": "Mason",
        "type": task_type,
        "task": task,
        "created_by": "Atlas",
        "created_at": now()
    }

    if file_path:
        new_task["file"] = file_path

    if "content" in context:
        new_task["content"] = context["content"]

    tasks.append(new_task)
    save_queue(tasks)

    return new_task


def run_mason_once():
    from agents.mason_worker import process_once
    return process_once()


def latest_report_preview(limit=3000):
    reports = sorted(REPORTS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not reports:
        return None

    latest = reports[0]
    return {
        "report": str(latest),
        "preview": latest.read_text(encoding="utf-8", errors="replace")[-limit:]
    }


def mason_agent(task="", context=None):
    context = context or {}

    execute_now = context.get("execute_now", True)

    queued = create_mason_task(task, context)

    response = {
        "agent": "Mason",
        "role": "Kingdom Architect and Foreman Builder",
        "status": "queued",
        "message": "Mason heard the command and created a work order.",
        "queued_task": queued,
        "timestamp": now()
    }

    if execute_now:
        did_work = run_mason_once()
        response["status"] = "executed" if did_work else "queued_no_pending_work"
        response["mason_worker_ran"] = did_work
        response["latest_report"] = latest_report_preview()

    return response


if __name__ == "__main__":
    print(mason_agent("Mason verify all agents", {"execute_now": True}))
'''

atlas_bridge_code = r'''from pathlib import Path
import sys
from datetime import datetime

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\PUTER")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

AGENT_MAP = {
    "mason": ("skills.mason_agent", "mason_agent"),
    "hunter": ("skills.hunter_agent", "hunter_agent"),
    "gideon": ("skills.gideon_agent", "gideon_agent"),
    "amanda": ("skills.amanda_agent", "amanda_agent"),
    "david": ("skills.david_agent", "david_agent"),
    "ranger": ("skills.ranger_agent", "ranger_agent"),
    "scout": ("skills.scout_agent", "scout_agent"),
    "micah": ("skills.micah_agent", "micah_agent"),
    "taylor": ("skills.taylor_agent", "taylor_agent"),
}


def detect_agent(text):
    text = (text or "").lower()
    for agent_name in AGENT_MAP:
        if agent_name in text:
            return agent_name
    return None


def delegate_to_agent(task="", context=None):
    context = context or {}
    agent_name = (context.get("agent") or detect_agent(task) or "").lower()

    if not agent_name:
        return {
            "status": "needs_agent",
            "message": "Atlas needs an agent name.",
            "available_agents": sorted(AGENT_MAP.keys())
        }

    if agent_name not in AGENT_MAP:
        return {
            "status": "unknown_agent",
            "requested_agent": agent_name,
            "available_agents": sorted(AGENT_MAP.keys())
        }

    module_name, function_name = AGENT_MAP[agent_name]
    module = __import__(module_name, fromlist=[function_name])
    agent_function = getattr(module, function_name)

    return {
        "status": "delegated",
        "delegated_to": agent_name.title(),
        "task": task,
        "result": agent_function(task, context),
        "timestamp": datetime.now().isoformat(timespec="seconds")
    }


def atlas_command(task="", context=None):
    return delegate_to_agent(task, context)


if __name__ == "__main__":
    result = atlas_command("Atlas, have Mason verify all agents", {"agent": "mason", "execute_now": True})
    print(result)
'''

test_code = r'''from pathlib import Path
import sys

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\PUTER")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.atlas_agent_delegation import atlas_command

result = atlas_command("Atlas, have Mason verify all agents", {"agent": "mason", "execute_now": True})

assert result["status"] == "delegated", result
assert result["delegated_to"] == "Mason", result
assert result["result"]["agent"] == "Mason", result
assert result["result"]["status"] in ["executed", "queued"], result

print("ATLAS CAN SPEAK TO MASON: PASS")
print(result)
'''

(SKILLS_DIR / "mason_agent.py").write_text(mason_agent_code, encoding="utf-8")
(AGENTS_DIR / "atlas_agent_delegation.py").write_text(atlas_bridge_code, encoding="utf-8")
(AGENTS_DIR / "test_atlas_to_mason.py").write_text(test_code, encoding="utf-8")

print("Mason ears, eyes, tongue, and Atlas bridge installed.")
