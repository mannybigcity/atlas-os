from pathlib import Path
import json

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\PUTER")
SKILLS_DIR = PROJECT_ROOT / "skills"
QUEUE_FILE = PROJECT_ROOT / "mason_workspace" / "mason_task_queue.json"

builder_code = r'''
from pathlib import Path
import sys
import json
import subprocess
from datetime import datetime

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\PUTER")
SKILLS_DIR = PROJECT_ROOT / "skills"
WORKSPACE = PROJECT_ROOT / "mason_workspace"
REPORTS_DIR = WORKSPACE / "reports"
MEMORY_FILE = WORKSPACE / "mason_memory.json"

for p in [SKILLS_DIR, WORKSPACE, REPORTS_DIR]:
    p.mkdir(parents=True, exist_ok=True)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


PROJECT_PLANNER_CODE = r'''from datetime import datetime

def mason_project_planner(goal="", context=None):
    context = context or {}
    text = (goal or "").lower()

    if "crm" in text:
        mission_type = "build_crm"
        steps = [
            "Inspect existing CRM/customer files.",
            "Create CRM data model for customers, follow-ups, opportunities, and notes.",
            "Build CRM starter module.",
            "Add follow-up priority logic.",
            "Run CRM self-test.",
            "Report CRM status to Atlas."
        ]
    elif "taylor" in text or "website" in text:
        mission_type = "redesign_taylor"
        steps = [
            "Inspect Taylor agent.",
            "Define Taylor website-builder standards.",
            "Rewrite Taylor with page audit, landing page plan, copy sections, and CTA logic.",
            "Run Taylor self-test.",
            "Report Taylor status to Atlas."
        ]
    elif "memory" in text or "atlas memory" in text:
        mission_type = "upgrade_atlas_memory"
        steps = [
            "Inspect Atlas memory files.",
            "Design memory router categories.",
            "Build memory upgrade plan.",
            "Create starter memory manager.",
            "Run memory self-test.",
            "Report memory status to Atlas."
        ]
    elif "hunter" in text or "lead" in text:
        mission_type = "hunter_auto_leads"
        steps = [
            "Inspect Hunter agent.",
            "Define lead source structure.",
            "Build automatic lead intake and scoring starter.",
            "Run Hunter lead self-test.",
            "Report Hunter status to Atlas."
        ]
    else:
        mission_type = "general_build"
        steps = [
            "Inspect relevant files.",
            "Create build plan.",
            "Write safe starter module.",
            "Run self-test.",
            "Report result to Atlas."
        ]

    return {
        "agent": "Mason",
        "skill": "Project Planner",
        "status": "planned",
        "goal": goal,
        "mission_type": mission_type,
        "steps": steps,
        "timestamp": datetime.now().isoformat(timespec="seconds")
    }

if __name__ == "__main__":
    print(mason_project_planner("Atlas, have Mason build a CRM"))
'''


MISSION_RUNNER_CODE = r'''from pathlib import Path
import sys
import json
import subprocess
from datetime import datetime

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\PUTER")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

WORKSPACE = PROJECT_ROOT / "mason_workspace"
REPORTS_DIR = WORKSPACE / "reports"
MEMORY_FILE = WORKSPACE / "mason_memory.json"

from skills.mason_project_planner import mason_project_planner


def now():
    return datetime.now().isoformat(timespec="seconds")


def save_memory(entry):
    if MEMORY_FILE.exists():
        data = json.loads(MEMORY_FILE.read_text(encoding="utf-8-sig"))
    else:
        data = []
    data.append(entry)
    MEMORY_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def run_python(path):
    result = subprocess.run(
        [sys.executable, str(path)],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True
    )
    return {
        "file": str(path),
        "returncode": result.returncode,
        "success": result.returncode == 0,
        "stdout": result.stdout[-4000:],
        "stderr": result.stderr[-4000:]
    }


def build_crm_starter():
    path = PROJECT_ROOT / "skills" / "david_crm_engine.py"
    code = '''from datetime import datetime

def david_crm_engine(customers=None):
    customers = customers or []
    followups = []
    for customer in customers:
        urgency = int(customer.get("urgency", 5) or 5)
        days = int(customer.get("days_since_contact", 0) or 0)
        value = int(customer.get("value", 0) or 0)
        score = urgency * 10 + days * 4 + value
        followups.append({
            "name": customer.get("name", "Unnamed customer"),
            "score": score,
            "next_action": customer.get("next_action", "Follow up."),
            "priority": "HIGH" if score >= 100 else "NORMAL"
        })
    followups.sort(key=lambda x: x["score"], reverse=True)
    return {
        "status": "success",
        "engine": "David CRM Engine",
        "followups": followups,
        "timestamp": datetime.now().isoformat(timespec="seconds")
    }

if __name__ == "__main__":
    print(david_crm_engine([{"name": "Kandy", "urgency": 8, "days_since_contact": 2, "value": 419}]))
'''
    path.write_text(code, encoding="utf-8")
    return run_python(path)


def build_taylor_redesign():
    path = PROJECT_ROOT / "skills" / "taylor_agent.py"
    code = '''from datetime import datetime

AGENT_NAME = "Taylor"
AGENT_ROLE = "Website Builder"

def taylor_agent(task="", context=None):
    context = context or {}
    page = context.get("page", "home page")
    business = context.get("business", "SIS Custom Creations")
    goal = context.get("goal", "turn visitors into customers")

    audit = [
        "Clear headline that explains the offer fast.",
        "Service sections for parties, workshops, custom items, and business solutions.",
        "Trust section with photos, examples, testimonials, or process.",
        "Strong call-to-action above the fold and at the bottom.",
        "Mobile-first layout with short copy.",
        "Simple quote/contact path."
    ]

    return {
        "agent": AGENT_NAME,
        "role": AGENT_ROLE,
        "status": "success",
        "task": task,
        "business": business,
        "page": page,
        "goal": goal,
        "website_audit": audit,
        "recommended_next_action": "Send Taylor the page copy or screenshot for a full rewrite.",
        "timestamp": datetime.now().isoformat(timespec="seconds")
    }

if __name__ == "__main__":
    print(taylor_agent("Redesign SIS page", {"page": "SIS home page"}))
'''
    path.write_text(code, encoding="utf-8")
    return run_python(path)


def build_memory_manager():
    path = PROJECT_ROOT / "skills" / "atlas_memory_manager.py"
    code = '''from pathlib import Path
import json
from datetime import datetime

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\PUTER")
MEMORY_FILE = PROJECT_ROOT / "mason_workspace" / "atlas_memory_manager_log.json"

def atlas_memory_manager(memory_type="", content="", priority=5):
    if MEMORY_FILE.exists():
        data = json.loads(MEMORY_FILE.read_text(encoding="utf-8-sig"))
    else:
        data = []

    entry = {
        "memory_type": memory_type or "general",
        "content": content,
        "priority": priority,
        "timestamp": datetime.now().isoformat(timespec="seconds")
    }
    data.append(entry)
    MEMORY_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

    return {
        "status": "success",
        "saved": entry,
        "total_memories": len(data)
    }

if __name__ == "__main__":
    print(atlas_memory_manager("kingdom", "Atlas memory manager starter operational.", 8))
'''
    path.write_text(code, encoding="utf-8")
    return run_python(path)


def build_hunter_leads():
    path = PROJECT_ROOT / "skills" / "hunter_lead_engine.py"
    code = '''from datetime import datetime

def hunter_lead_engine(leads=None):
    leads = leads or []
    ranked = []
    for lead in leads:
        value = int(lead.get("value", 0) or 0)
        urgency = int(lead.get("urgency", 5) or 5)
        fit = int(lead.get("fit", 5) or 5)
        access = int(lead.get("access", 5) or 5)
        score = value + urgency * 12 + fit * 10 + access * 8
        ranked.append({
            "name": lead.get("name", "Unnamed lead"),
            "score": score,
            "source": lead.get("source", "unknown"),
            "recommendation": "CONTACT FIRST" if score >= 300 else "RESEARCH" if score >= 120 else "LOW PRIORITY"
        })
    ranked.sort(key=lambda x: x["score"], reverse=True)
    return {
        "status": "success",
        "engine": "Hunter Lead Engine",
        "ranked_leads": ranked,
        "timestamp": datetime.now().isoformat(timespec="seconds")
    }

if __name__ == "__main__":
    print(hunter_lead_engine([{"name": "Local HVAC company", "value": 500, "urgency": 7, "fit": 9, "access": 6, "source": "manual"}]))
'''
    path.write_text(code, encoding="utf-8")
    return run_python(path)


def mason_mission_runner(goal="", context=None):
    context = context or {}
    plan = mason_project_planner(goal, context)
    mission_type = plan["mission_type"]

    if mission_type == "build_crm":
        result = build_crm_starter()
    elif mission_type == "redesign_taylor":
        result = build_taylor_redesign()
    elif mission_type == "upgrade_atlas_memory":
        result = build_memory_manager()
    elif mission_type == "hunter_auto_leads":
        result = build_hunter_leads()
    else:
        result = {"success": False, "stdout": "", "stderr": "No mission builder found for this goal."}

    entry = {
        "goal": goal,
        "plan": plan,
        "result": result,
        "status": "complete" if result.get("success") else "failed",
        "timestamp": now()
    }
    save_memory(entry)

    report_path = REPORTS_DIR / f"mason_mission_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_path.write_text(json.dumps(entry, indent=2), encoding="utf-8")

    return {
        "agent": "Mason",
        "skill": "Mission Runner",
        "status": entry["status"],
        "goal": goal,
        "plan": plan,
        "result": result,
        "report": str(report_path),
        "timestamp": now()
    }

if __name__ == "__main__":
    tests = [
        "Atlas, have Mason build a CRM.",
        "Atlas, have Mason completely redesign Taylor.",
        "Atlas, have Mason rewrite Atlas memory system.",
        "Atlas, have Mason make Hunter find leads automatically."
    ]
    for t in tests:
        r = mason_mission_runner(t)
        print(t, "=>", r["status"])
'''


MASON_AGENT_CODE = r'''from pathlib import Path
import sys
import json
from datetime import datetime

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\PUTER")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

WORKSPACE = PROJECT_ROOT / "mason_workspace"
QUEUE_FILE = WORKSPACE / "mason_task_queue.json"
REPORTS_DIR = WORKSPACE / "reports"

from skills.mason_mission_runner import mason_mission_runner

WORKSPACE.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def now():
    return datetime.now().isoformat(timespec="seconds")


def mason_agent(task="", context=None):
    context = context or {}

    big_goal_keywords = [
        "completely redesign",
        "build a crm",
        "rewrite atlas",
        "memory system",
        "find leads automatically",
        "build crm",
        "redesign taylor",
        "strengthen"
    ]

    lowered = (task or "").lower()

    if any(k in lowered for k in big_goal_keywords):
        result = mason_mission_runner(task, context)
        return {
            "agent": "Mason",
            "role": "Kingdom Architect and Foreman Builder",
            "status": result["status"],
            "message": "Mason planned and executed the mission.",
            "mission": result,
            "timestamp": now()
        }

    return {
        "agent": "Mason",
        "role": "Kingdom Architect and Foreman Builder",
        "status": "ready",
        "message": "Mason heard the command, but this command needs a known mission type or a build goal.",
        "examples": [
            "Atlas, have Mason build a CRM.",
            "Atlas, have Mason completely redesign Taylor.",
            "Atlas, have Mason rewrite Atlas memory system.",
            "Atlas, have Mason make Hunter find leads automatically."
        ],
        "timestamp": now()
    }

if __name__ == "__main__":
    print(mason_agent("Atlas, have Mason build a CRM."))
'''


TEST_CODE = r'''from pathlib import Path
import sys

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\PUTER")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from skills.mason_agent import mason_agent

tests = [
    "Atlas, have Mason completely redesign Taylor.",
    "Atlas, have Mason build a CRM.",
    "Atlas, have Mason rewrite Atlas memory system.",
    "Atlas, have Mason make Hunter find leads automatically."
]

for t in tests:
    result = mason_agent(t)
    assert result["status"] == "complete", result
    print(t)
    print("PASS")

print("MASON BRAIN MISSIONS VERIFIED")
'''


def write(path, code):
    path.write_text(code, encoding="utf-8")
    return str(path)


def run(path):
    result = subprocess.run([sys.executable, str(path)], cwd=str(PROJECT_ROOT), capture_output=True, text=True)
    return result


def main():
    files = [
        write(SKILLS_DIR / "mason_project_planner.py", PROJECT_PLANNER_CODE),
        write(SKILLS_DIR / "mason_mission_runner.py", MISSION_RUNNER_CODE),
        write(SKILLS_DIR / "mason_agent.py", MASON_AGENT_CODE),
        write(SKILLS_DIR / "test_mason_brain_missions.py", TEST_CODE),
    ]

    test = run(SKILLS_DIR / "test_mason_brain_missions.py")

    report = {
        "status": "complete" if test.returncode == 0 else "failed",
        "files_written": files,
        "test_stdout": test.stdout,
        "test_stderr": test.stderr,
        "timestamp": datetime.now().isoformat(timespec="seconds")
    }

    report_path = REPORTS_DIR / f"mason_brain_builder_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(test.stdout)
    print(test.stderr)
    print("STATUS:", report["status"].upper())
    print("REPORT:", report_path)

if __name__ == "__main__":
    main()
'''

(SKILLS_DIR / "mason_brain_builder.py").write_text(builder_code, encoding="utf-8")

QUEUE_FILE.write_text(json.dumps([
    {
        "id": "phase5_mason_brain",
        "status": "pending",
        "agent": "Mason",
        "type": "run_python",
        "file": str(SKILLS_DIR / "mason_brain_builder.py"),
        "task": "Build Mason project planner, mission runner, memory, verifier starter, and big-goal execution brain."
    }
], indent=2), encoding="utf-8")

print("Mason brain build mission loaded.")
