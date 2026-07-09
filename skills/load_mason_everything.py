from pathlib import Path
import json

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\PUTER")
SKILLS = PROJECT_ROOT / "skills"
QUEUE = PROJECT_ROOT / "mason_workspace" / "mason_task_queue.json"
SKILLS.mkdir(parents=True, exist_ok=True)

code = r'''
from pathlib import Path
import sys
import json
import subprocess
from datetime import datetime

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\PUTER")
SKILLS = PROJECT_ROOT / "skills"
WORKSPACE = PROJECT_ROOT / "mason_workspace"
REPORTS = WORKSPACE / "reports"
MEMORY = WORKSPACE / "mason_memory.json"

for p in [SKILLS, WORKSPACE, REPORTS]:
    p.mkdir(parents=True, exist_ok=True)

def write(name, content):
    path = SKILLS / name
    path.write_text(content, encoding="utf-8")
    return str(path)

write("mason_capability_registry.py", r"""
def mason_capability_registry():
    return {
        "can_write_files": True,
        "can_read_files": True,
        "can_run_python": True,
        "can_verify_outputs": True,
        "can_retry_failed_tasks": True,
        "can_plan_projects": True,
        "can_store_memory": True,
        "can_report_to_atlas": True,
        "allowed_dirs": ["agents", "skills", "ui", "mason_workspace"],
        "approval_required_for": ["external_messages", "money_actions", "deleting_files", "customer_contact"]
    }
""")

write("mason_memory.py", r"""
from pathlib import Path
import json
from datetime import datetime

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\PUTER")
MEMORY_FILE = PROJECT_ROOT / "mason_workspace" / "mason_memory.json"
MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)

def mason_remember(entry):
    if MEMORY_FILE.exists():
        data = json.loads(MEMORY_FILE.read_text(encoding="utf-8-sig"))
    else:
        data = []
    entry["timestamp"] = datetime.now().isoformat(timespec="seconds")
    data.append(entry)
    MEMORY_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return {"status": "remembered", "total": len(data), "entry": entry}

def mason_recall(limit=10):
    if not MEMORY_FILE.exists():
        return []
    return json.loads(MEMORY_FILE.read_text(encoding="utf-8-sig"))[-limit:]
""")

write("mason_verifier.py", r"""
from pathlib import Path
import sys
import subprocess

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\PUTER")

def verify_file_exists(path):
    path = Path(path)
    return {"check": "file_exists", "file": str(path), "success": path.exists()}

def verify_python(path, expected_text=None):
    path = Path(path)
    if not path.exists():
        return {"success": False, "error": "file missing", "file": str(path)}
    result = subprocess.run([sys.executable, str(path)], cwd=str(PROJECT_ROOT), capture_output=True, text=True)
    success = result.returncode == 0
    if expected_text:
        success = success and expected_text in result.stdout
    return {
        "check": "python_execution",
        "file": str(path),
        "success": success,
        "returncode": result.returncode,
        "stdout": result.stdout[-4000:],
        "stderr": result.stderr[-4000:],
        "expected_text": expected_text
    }

def mason_verify(target_file=None, expected_text=None):
    checks = []
    if target_file:
        checks.append(verify_file_exists(target_file))
        if str(target_file).endswith(".py"):
            checks.append(verify_python(target_file, expected_text))
    passed = all(c.get("success") for c in checks)
    return {"status": "passed" if passed else "failed", "checks": checks}
""")

write("mason_retry_engine.py", r"""
from skills.mason_verifier import verify_python

def mason_retry_python(path, expected_text=None, max_attempts=2):
    attempts = []
    for attempt in range(1, max_attempts + 1):
        result = verify_python(path, expected_text)
        result["attempt"] = attempt
        attempts.append(result)
        if result["success"]:
            return {"status": "success", "attempts": attempts}
    return {"status": "failed", "attempts": attempts, "note": "Retry engine can detect failures; auto-rewrite repair comes next."}
""")

write("mason_project_planner.py", r"""
from datetime import datetime

def mason_project_planner(goal="", context=None):
    text = (goal or "").lower()
    if "crm" in text:
        mission = "build_crm"
        steps = ["inspect CRM needs", "build CRM engine", "test CRM", "verify output", "report to Atlas"]
    elif "taylor" in text or "website" in text:
        mission = "redesign_taylor"
        steps = ["inspect Taylor", "rewrite Taylor as website builder", "test Taylor", "verify output", "report to Atlas"]
    elif "memory" in text:
        mission = "upgrade_memory"
        steps = ["build memory manager", "test save/recall", "verify output", "report to Atlas"]
    elif "hunter" in text or "leads" in text:
        mission = "hunter_leads"
        steps = ["build Hunter lead engine", "test lead scoring", "verify output", "report to Atlas"]
    else:
        mission = "general"
        steps = ["plan", "build", "test", "verify", "report"]
    return {"status": "planned", "goal": goal, "mission": mission, "steps": steps, "timestamp": datetime.now().isoformat(timespec="seconds")}
""")

write("mason_atlas_reporter.py", r"""
def mason_atlas_reporter(result):
    status = result.get("status", "unknown")
    goal = result.get("goal", "unknown mission")
    report = result.get("report", "")
    verification = result.get("verification", {})
    return {
        "status": status,
        "atlas_message": f"Mason completed mission: {goal}. Status: {status}. Verification: {verification.get('status', 'not provided')}.",
        "report": report,
        "raw": result
    }
""")

write("mason_mission_runner.py", r"""
from pathlib import Path
import sys
import json
from datetime import datetime

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\PUTER")
SKILLS = PROJECT_ROOT / "skills"
REPORTS = PROJECT_ROOT / "mason_workspace" / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)

from skills.mason_project_planner import mason_project_planner
from skills.mason_verifier import mason_verify
from skills.mason_retry_engine import mason_retry_python
from skills.mason_memory import mason_remember
from skills.mason_atlas_reporter import mason_atlas_reporter

def write(path, content):
    path = Path(path)
    path.write_text(content, encoding="utf-8")
    return str(path)

def build_crm():
    path = SKILLS / "david_crm_engine.py"
    write(path, '''from datetime import datetime
def david_crm_engine(customers=None):
    customers = customers or []
    ranked = []
    for c in customers:
        score = int(c.get("value",0)) + int(c.get("urgency",5))*10 + int(c.get("days_since_contact",0))*4
        ranked.append({"name": c.get("name","Unnamed"), "score": score, "next_action": c.get("next_action","Follow up")})
    ranked.sort(key=lambda x:x["score"], reverse=True)
    return {"status":"success","engine":"David CRM","followups":ranked,"timestamp":datetime.now().isoformat(timespec="seconds")}
if __name__=="__main__":
    print(david_crm_engine([{"name":"Kandy","value":419,"urgency":8,"days_since_contact":2}]))
''')
    return path, "David CRM"

def build_taylor():
    path = SKILLS / "taylor_agent.py"
    write(path, '''from datetime import datetime
def taylor_agent(task="", context=None):
    context = context or {}
    return {"agent":"Taylor","status":"success","role":"Website Builder","audit":["headline","services","proof","CTA","mobile layout"],"next_action":"Send page copy or screenshot.","timestamp":datetime.now().isoformat(timespec="seconds")}
if __name__=="__main__":
    print(taylor_agent("test"))
''')
    return path, "Website Builder"

def build_memory():
    path = SKILLS / "atlas_memory_manager.py"
    write(path, '''from pathlib import Path
import json
from datetime import datetime
FILE = Path(r"C:\\Users\\User\\Desktop\\PUTER\\mason_workspace\\atlas_memory_manager_log.json")
def atlas_memory_manager(content="", memory_type="general", priority=5):
    data = json.loads(FILE.read_text(encoding="utf-8-sig")) if FILE.exists() else []
    entry = {"content":content,"memory_type":memory_type,"priority":priority,"timestamp":datetime.now().isoformat(timespec="seconds")}
    data.append(entry)
    FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return {"status":"success","saved":entry,"total":len(data)}
if __name__=="__main__":
    print(atlas_memory_manager("memory manager online","kingdom",8))
''')
    return path, "memory manager online"

def build_hunter():
    path = SKILLS / "hunter_lead_engine.py"
    write(path, '''from datetime import datetime
def hunter_lead_engine(leads=None):
    leads = leads or []
    ranked = []
    for l in leads:
        score = int(l.get("value",0)) + int(l.get("fit",5))*10 + int(l.get("urgency",5))*12
        ranked.append({"name":l.get("name","Unnamed"),"score":score,"recommendation":"CONTACT FIRST" if score>=250 else "RESEARCH"})
    ranked.sort(key=lambda x:x["score"], reverse=True)
    return {"status":"success","engine":"Hunter Lead Engine","ranked_leads":ranked,"timestamp":datetime.now().isoformat(timespec="seconds")}
if __name__=="__main__":
    print(hunter_lead_engine([{"name":"Local HVAC","value":500,"fit":9,"urgency":7}]))
''')
    return path, "Hunter Lead Engine"

def mason_mission_runner(goal="", context=None):
    plan = mason_project_planner(goal, context)
    mission = plan["mission"]

    if mission == "build_crm":
        path, expected = build_crm()
    elif mission == "redesign_taylor":
        path, expected = build_taylor()
    elif mission == "upgrade_memory":
        path, expected = build_memory()
    elif mission == "hunter_leads":
        path, expected = build_hunter()
    else:
        path, expected = build_crm()

    verification = mason_verify(path, expected)
    retry = None
    if verification["status"] != "passed":
        retry = mason_retry_python(path, expected)
        verification = mason_verify(path, expected)

    result = {
        "status": "complete" if verification["status"] == "passed" else "failed",
        "goal": goal,
        "plan": plan,
        "built_file": str(path),
        "verification": verification,
        "retry": retry,
        "timestamp": datetime.now().isoformat(timespec="seconds")
    }

    mason_remember({"type": "mission", "result": result})
    report_path = REPORTS / f"mason_full_foreman_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    result["report"] = str(report_path)
    return mason_atlas_reporter(result)

if __name__ == "__main__":
    for goal in [
        "Atlas, have Mason build a CRM.",
        "Atlas, have Mason completely redesign Taylor.",
        "Atlas, have Mason rewrite Atlas memory system.",
        "Atlas, have Mason make Hunter find leads automatically."
    ]:
        print(mason_mission_runner(goal)["atlas_message"])
""")

write("mason_agent.py", r"""
from datetime import datetime
from skills.mason_capability_registry import mason_capability_registry
from skills.mason_mission_runner import mason_mission_runner
from skills.mason_memory import mason_recall

def mason_agent(task="", context=None):
    context = context or {}
    text = (task or "").lower()

    if "capabilities" in text or "what can you do" in text:
        return {"agent":"Mason","status":"success","capabilities":mason_capability_registry()}

    if "memory" in text and "recall" in text:
        return {"agent":"Mason","status":"success","memory":mason_recall()}

    result = mason_mission_runner(task, context)
    return {"agent":"Mason","status":result["status"],"message":result["atlas_message"],"result":result,"timestamp":datetime.now().isoformat(timespec="seconds")}
""")

test = SKILLS / "test_mason_full_foreman.py"
test.write_text(r"""
from skills.mason_agent import mason_agent

goals = [
    "Atlas, have Mason build a CRM.",
    "Atlas, have Mason completely redesign Taylor.",
    "Atlas, have Mason rewrite Atlas memory system.",
    "Atlas, have Mason make Hunter find leads automatically."
]

for goal in goals:
    r = mason_agent(goal)
    assert r["status"] == "complete", r
    print(goal, "PASS")

print("MASON FULL FOREMAN VERIFIED")
""", encoding="utf-8")

result = subprocess.run([sys.executable, str(test)], cwd=str(PROJECT_ROOT), capture_output=True, text=True)
report = REPORTS / f"mason_everything_builder_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
report.write_text(json.dumps({"stdout":result.stdout,"stderr":result.stderr,"returncode":result.returncode}, indent=2), encoding="utf-8")

print(result.stdout)
print(result.stderr)
print("STATUS:", "COMPLETE" if result.returncode == 0 else "FAILED")
print("REPORT:", report)
'''

(SKILLS / "mason_everything_builder.py").write_text(code, encoding="utf-8")

QUEUE.write_text(json.dumps([{
    "id": "phase6_give_mason_everything",
    "status": "pending",
    "agent": "Mason",
    "type": "run_python",
    "file": str(SKILLS / "mason_everything_builder.py"),
    "task": "Give Mason full foreman system: planner, runner, verifier, retry engine, memory, capability registry, and Atlas reporter."
}], indent=2), encoding="utf-8")

print("Full Mason Foreman mission loaded.")
