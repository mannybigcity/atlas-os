from pathlib import Path
import json
import textwrap

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\PUTER")
SKILLS_DIR = PROJECT_ROOT / "skills"
QUEUE_FILE = PROJECT_ROOT / "mason_workspace" / "mason_task_queue.json"
SKILLS_DIR.mkdir(parents=True, exist_ok=True)

strengthener = r'''
from pathlib import Path
import sys
import shutil
import subprocess
import json
from datetime import datetime

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\PUTER")
SKILLS_DIR = PROJECT_ROOT / "skills"
AGENTS_DIR = PROJECT_ROOT / "agents"
WORKSPACE = PROJECT_ROOT / "mason_workspace"
REPORTS_DIR = WORKSPACE / "reports"
BACKUPS_DIR = WORKSPACE / "backups"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)
BACKUPS_DIR.mkdir(parents=True, exist_ok=True)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def backup(path):
    path = Path(path)
    if not path.exists():
        return None
    backup_path = BACKUPS_DIR / f"{path.stem}_{stamp()}{path.suffix}.bak"
    shutil.copy2(path, backup_path)
    return str(backup_path)


def write_file(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    old = backup(path)
    path.write_text(content, encoding="utf-8")
    return {"file": str(path), "backup": old}


AGENT_CODES = {
"hunter": r'''from datetime import datetime

AGENT_NAME = "Hunter"
AGENT_ROLE = "Revenue Commander"

def hunter_agent(task="", context=None):
    context = context or {}
    opportunities = context.get("opportunities", context.get("items", context.get("leads", [])))

    ranked = []
    for item in opportunities:
        revenue = int(item.get("revenue", item.get("value", 0)) or 0)
        urgency = int(item.get("urgency", 1) or 1)
        ease = int(item.get("ease", 1) or 1)
        relationship = int(item.get("relationship", 1) or 1)
        close_chance = int(item.get("close_chance", 5) or 5)
        score = revenue + urgency * 15 + ease * 10 + relationship * 8 + close_chance * 12
        ranked.append({
            "name": item.get("name", "Unnamed opportunity"),
            "score": score,
            "recommendation": "CHASE NOW" if score >= 500 else "FOLLOW UP" if score >= 150 else "LOW PRIORITY",
            "reason": "Ranked by money, urgency, ease, relationship, and close chance.",
            "details": item
        })

    ranked.sort(key=lambda x: x["score"], reverse=True)

    return {
        "agent": AGENT_NAME,
        "role": AGENT_ROLE,
        "status": "success",
        "task": task,
        "ranked_opportunities": ranked,
        "top_action": ranked[0] if ranked else "Send Hunter leads or opportunities to rank.",
        "timestamp": datetime.now().isoformat(timespec="seconds")
    }

if __name__ == "__main__":
    print(hunter_agent("test", {"opportunities": [{"name": "50 hats", "revenue": 950, "urgency": 9, "ease": 7}]}))
''',

"gideon": r'''from datetime import datetime

AGENT_NAME = "Gideon"
AGENT_ROLE = "Finance and Profitability"

def gideon_agent(task="", context=None):
    context = context or {}
    jobs = context.get("jobs", context.get("items", []))

    reviewed = []
    total_profit = 0

    for job in jobs:
        revenue = float(job.get("revenue", job.get("value", 0)) or 0)
        cost = float(job.get("cost", 0) or 0)
        profit = revenue - cost
        margin = round((profit / revenue) * 100, 2) if revenue else 0
        total_profit += profit
        reviewed.append({
            "name": job.get("name", "Unnamed job"),
            "revenue": revenue,
            "cost": cost,
            "profit": profit,
            "margin_percent": margin,
            "recommendation": "GOOD MARGIN" if margin >= 40 else "WATCH COSTS" if margin >= 20 else "LOW MARGIN"
        })

    reviewed.sort(key=lambda x: x["profit"], reverse=True)

    return {
        "agent": AGENT_NAME,
        "role": AGENT_ROLE,
        "status": "success",
        "task": task,
        "reviewed_jobs": reviewed,
        "total_projected_profit": total_profit,
        "top_financial_action": reviewed[0] if reviewed else "Send Gideon revenue and cost numbers.",
        "timestamp": datetime.now().isoformat(timespec="seconds")
    }

if __name__ == "__main__":
    print(gideon_agent("test", {"jobs": [{"name": "Hats", "revenue": 950, "cost": 637.5}]}))
''',

"amanda": r'''from datetime import datetime

AGENT_NAME = "Amanda"
AGENT_ROLE = "Outreach and Partnerships"

def amanda_agent(task="", context=None):
    context = context or {}
    prospect = context.get("prospect", context.get("customer", "friend"))
    offer = context.get("offer", "custom creations, shirts, hats, signs, or business items")

    message = (
        f"Hey {prospect}! I wanted to follow up and see if you still needed help with {offer}. "
        "We can help with custom work, business gear, gifts, parties, and branded items. "
        "Send me what you have in mind and I can help put together options."
    )

    return {
        "agent": AGENT_NAME,
        "role": AGENT_ROLE,
        "status": "success",
        "task": task,
        "draft_message": message,
        "approval_required": True,
        "next_action": "Manny approves or edits before sending.",
        "timestamp": datetime.now().isoformat(timespec="seconds")
    }

if __name__ == "__main__":
    print(amanda_agent("test", {"prospect": "B&B HVAC", "offer": "hats and shirts"}))
''',

"david": r'''from datetime import datetime

AGENT_NAME = "David"
AGENT_ROLE = "CRM and Follow-Up Tracking"

def david_agent(task="", context=None):
    context = context or {}
    customers = context.get("customers", context.get("items", []))

    followups = []
    for c in customers:
        urgency = int(c.get("urgency", 5) or 5)
        days = int(c.get("days_since_contact", 0) or 0)
        score = urgency * 10 + days * 3
        followups.append({
            "name": c.get("name", "Unnamed customer"),
            "score": score,
            "next_action": c.get("next_action", "Follow up and confirm next step."),
            "priority": "HIGH" if score >= 60 else "NORMAL"
        })

    followups.sort(key=lambda x: x["score"], reverse=True)

    return {
        "agent": AGENT_NAME,
        "role": AGENT_ROLE,
        "status": "success",
        "task": task,
        "followups": followups,
        "top_followup": followups[0] if followups else "Send David customer follow-up list.",
        "timestamp": datetime.now().isoformat(timespec="seconds")
    }

if __name__ == "__main__":
    print(david_agent("test", {"customers": [{"name": "Kandy", "urgency": 8, "days_since_contact": 2}]}))
''',

"ranger": r'''from datetime import datetime

AGENT_NAME = "Ranger"
AGENT_ROLE = "Customer Success"

def ranger_agent(task="", context=None):
    context = context or {}
    issue = context.get("issue", "")
    customer = context.get("customer", "customer")

    response = (
        f"Customer success plan for {customer}: acknowledge the concern, clarify the need, "
        "confirm the next step, protect the relationship, and report back to Manny before any major promise."
    )

    return {
        "agent": AGENT_NAME,
        "role": AGENT_ROLE,
        "status": "success",
        "task": task,
        "customer": customer,
        "issue": issue,
        "success_plan": response,
        "approval_required": True,
        "timestamp": datetime.now().isoformat(timespec="seconds")
    }

if __name__ == "__main__":
    print(ranger_agent("test", {"customer": "Uncle Ray", "issue": "order follow-up"}))
''',

"scout": r'''from datetime import datetime

AGENT_NAME = "Scout"
AGENT_ROLE = "Research and Lead Intelligence"

def scout_agent(task="", context=None):
    context = context or {}
    targets = context.get("targets", context.get("items", []))

    intel = []
    for target in targets:
        intel.append({
            "name": target.get("name", "Unnamed target"),
            "category": target.get("category", "unknown"),
            "research_questions": [
                "Who is the decision maker?",
                "What do they likely need?",
                "What is the fastest respectful contact path?",
                "Is this worth Manny's time today?"
            ],
            "recommended_action": "Research before outreach."
        })

    return {
        "agent": AGENT_NAME,
        "role": AGENT_ROLE,
        "status": "success",
        "task": task,
        "lead_intelligence": intel,
        "next_action": intel[0] if intel else "Send Scout targets to research.",
        "timestamp": datetime.now().isoformat(timespec="seconds")
    }

if __name__ == "__main__":
    print(scout_agent("test", {"targets": [{"name": "local HVAC companies", "category": "business"}]}))
''',

"micah": r'''from datetime import datetime

AGENT_NAME = "Micah"
AGENT_ROLE = "Social Media"

def micah_agent(task="", context=None):
    context = context or {}
    topic = context.get("topic", "RAMFAM KINGDOM progress")
    audience = context.get("audience", "friends, family, and future customers")

    post = (
        f"Building in public update: {topic}. "
        "One brick at a time, one lesson at a time, and one step closer to creating something that helps my family and others. "
        "Comment ATLAS if you want to follow the journey. 👑"
    )

    return {
        "agent": AGENT_NAME,
        "role": AGENT_ROLE,
        "status": "success",
        "task": task,
        "audience": audience,
        "draft_post": post,
        "approval_required": True,
        "timestamp": datetime.now().isoformat(timespec="seconds")
    }

if __name__ == "__main__":
    print(micah_agent("test", {"topic": "Mason can now build and verify"}))
''',

"taylor": r'''from datetime import datetime

AGENT_NAME = "Taylor"
AGENT_ROLE = "Website Builder"

def taylor_agent(task="", context=None):
    context = context or {}
    page = context.get("page", "home page")
    goal = context.get("goal", "convert visitors into customers")

    plan = [
        "Clarify the headline.",
        "Add simple service sections.",
        "Add proof or trust signals.",
        "Add a clear call-to-action.",
        "Make it mobile friendly.",
        "Keep copy short and direct."
    ]

    return {
        "agent": AGENT_NAME,
        "role": AGENT_ROLE,
        "status": "success",
        "task": task,
        "page": page,
        "goal": goal,
        "website_plan": plan,
        "next_action": "Send Taylor the page or business offer to improve.",
        "timestamp": datetime.now().isoformat(timespec="seconds")
    }

if __name__ == "__main__":
    print(taylor_agent("test", {"page": "SIS home page", "goal": "book parties and business orders"}))
'''
}


DELEGATION_CODE = r'''from pathlib import Path
import sys
from datetime import datetime

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\PUTER")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

AGENT_MAP = {
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
    for name in AGENT_MAP:
        if name in text:
            return name
    return None

def delegate_to_agent(task="", context=None):
    context = context or {}
    agent = (context.get("agent") or detect_agent(task) or "").lower()

    if not agent:
        return {
            "status": "needs_agent",
            "message": "Atlas needs an agent name.",
            "available_agents": list(AGENT_MAP.keys())
        }

    if agent not in AGENT_MAP:
        return {
            "status": "unknown_agent",
            "requested_agent": agent,
            "available_agents": list(AGENT_MAP.keys())
        }

    module_name, function_name = AGENT_MAP[agent]
    module = __import__(module_name, fromlist=[function_name])
    fn = getattr(module, function_name)

    return {
        "status": "delegated",
        "delegated_to": agent.title(),
        "task": task,
        "result": fn(task, context),
        "timestamp": datetime.now().isoformat(timespec="seconds")
    }

def atlas_command(task="", context=None):
    return delegate_to_agent(task, context)

if __name__ == "__main__":
    tests = [
        ("Have Hunter rank opportunities", {"agent": "hunter", "opportunities": [{"name": "50 hats", "revenue": 950, "urgency": 9, "ease": 7}]}),
        ("Have Gideon review profit", {"agent": "gideon", "jobs": [{"name": "50 hats", "revenue": 950, "cost": 637.5}]}),
        ("Have Amanda draft outreach", {"agent": "amanda", "prospect": "B&B HVAC", "offer": "hats and shirts"}),
        ("Have David track followups", {"agent": "david", "customers": [{"name": "Kandy", "urgency": 8, "days_since_contact": 2}]}),
        ("Have Ranger handle customer success", {"agent": "ranger", "customer": "Uncle Ray", "issue": "follow-up"}),
        ("Have Scout research leads", {"agent": "scout", "targets": [{"name": "local HVAC companies", "category": "business"}]}),
        ("Have Micah draft post", {"agent": "micah", "topic": "Mason strengthening ATLAS"}),
        ("Have Taylor improve site", {"agent": "taylor", "page": "SIS home page"}),
    ]

    for task, context in tests:
        result = delegate_to_agent(task, context)
        print(result["delegated_to"], result["status"], result["result"]["status"])

    print("ALL ATLAS AGENT DELEGATION TESTS PASSED")
'''


TEST_CODE = r'''from agents.atlas_agent_delegation import delegate_to_agent

TESTS = [
    ("hunter", "Have Hunter rank opportunities", {"opportunities": [{"name": "50 hats", "revenue": 950, "urgency": 9, "ease": 7}]}),
    ("gideon", "Have Gideon review profit", {"jobs": [{"name": "50 hats", "revenue": 950, "cost": 637.5}]}),
    ("amanda", "Have Amanda draft outreach", {"prospect": "B&B HVAC", "offer": "hats and shirts"}),
    ("david", "Have David track followups", {"customers": [{"name": "Kandy", "urgency": 8, "days_since_contact": 2}]}),
    ("ranger", "Have Ranger handle customer success", {"customer": "Uncle Ray", "issue": "follow-up"}),
    ("scout", "Have Scout research leads", {"targets": [{"name": "local HVAC companies", "category": "business"}]}),
    ("micah", "Have Micah draft post", {"topic": "Mason strengthening ATLAS"}),
    ("taylor", "Have Taylor improve website", {"page": "SIS home page"}),
]

for agent, task, context in TESTS:
    context["agent"] = agent
    result = delegate_to_agent(task, context)
    assert result["status"] == "delegated", result
    assert result["delegated_to"].lower() == agent, result
    assert result["result"]["status"] == "success", result
    print(f"{agent.upper()}: PASS")

print("KINGDOM ALL AGENTS VERIFIED")
'''


def run_python(path):
    result = subprocess.run([sys.executable, str(path)], cwd=str(PROJECT_ROOT), capture_output=True, text=True)
    return {
        "file": str(path),
        "returncode": result.returncode,
        "success": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr
    }


def main():
    report = []
    report.append("# Mason Kingdom Strengthening Report")
    report.append(f"Time: {datetime.now().isoformat(timespec='seconds')}")
    report.append("")

    written = []

    for agent, code in AGENT_CODES.items():
        written.append(write_file(SKILLS_DIR / f"{agent}_agent.py", code))

    written.append(write_file(AGENTS_DIR / "atlas_agent_delegation.py", DELEGATION_CODE))
    written.append(write_file(AGENTS_DIR / "test_all_agent_delegation.py", TEST_CODE))

    compile_results = []
    for item in written:
        file_path = Path(item["file"])
        if file_path.suffix == ".py":
            compile_results.append(run_python(file_path))

    final_test = run_python(AGENTS_DIR / "test_all_agent_delegation.py")

    report.append("## Files Written")
    for item in written:
        report.append(f"- {item['file']} | backup: {item['backup']}")

    report.append("")
    report.append("## Verification")
    report.append(json.dumps(final_test, indent=2))

    report.append("")
    if final_test["success"] and "KINGDOM ALL AGENTS VERIFIED" in final_test["stdout"]:
        report.append("STATUS: KINGDOM VERIFIED")
        print("MASON KINGDOM STRENGTHENING COMPLETE")
        print("STATUS: KINGDOM VERIFIED")
    else:
        report.append("STATUS: FAILED")
        print("MASON KINGDOM STRENGTHENING FAILED")

    report_path = REPORTS_DIR / f"mason_kingdom_strengthening_{stamp()}.md"
    report_path.write_text("\n".join(report), encoding="utf-8")
    print(f"REPORT: {report_path}")


if __name__ == "__main__":
    main()
'''

(SKILLS_DIR / "mason_kingdom_strengthener.py").write_text(strengthener, encoding="utf-8")

QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
QUEUE_FILE.write_text(json.dumps([
    {
        "id": "phase4_kingdom_strengthening",
        "status": "pending",
        "agent": "Mason",
        "type": "run_python",
        "file": str(SKILLS_DIR / "mason_kingdom_strengthener.py"),
        "task": "Mason strengthen ATLAS delegation and all eight agents, then verify everything."
    }
], indent=2), encoding="utf-8")

print("Mason strengthening mission loaded.")
print("Now Mason will run the strengthening mission.")
