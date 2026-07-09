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


def backup_file(path):
    path = Path(path)
    if not path.exists():
        return None
    backup_path = BACKUPS_DIR / f"{path.stem}_{stamp()}{path.suffix}.bak"
    shutil.copy2(path, backup_path)
    return str(backup_path)


def write_file(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    old_backup = backup_file(path)
    path.write_text(content, encoding="utf-8")
    return {"file": str(path), "backup": old_backup}


AGENTS = {
    "hunter": {
        "role": "Revenue Commander",
        "focus": "Rank revenue opportunities by money, urgency, ease, relationship, and close chance."
    },
    "gideon": {
        "role": "Finance and Profitability",
        "focus": "Review revenue, cost, profit, cash flow, and margin."
    },
    "amanda": {
        "role": "Outreach and Partnerships",
        "focus": "Draft outreach, marketplace replies, partnership messages, and follow-up messages."
    },
    "david": {
        "role": "CRM and Follow-Up Tracking",
        "focus": "Track customers, follow-ups, next actions, and urgency."
    },
    "ranger": {
        "role": "Customer Success",
        "focus": "Protect relationships, handle issues, clarify next steps, and improve retention."
    },
    "scout": {
        "role": "Research and Lead Intelligence",
        "focus": "Research leads, targets, decision makers, and opportunity intelligence."
    },
    "micah": {
        "role": "Social Media",
        "focus": "Draft posts, captions, hooks, content ideas, and engagement strategy."
    },
    "taylor": {
        "role": "Website Builder",
        "focus": "Improve landing pages, website copy, page structure, and calls to action."
    },
}


def build_agent_code(agent_key, role, focus):
    function_name = f"{agent_key}_agent"
    agent_title = agent_key.title()

    return f'''from datetime import datetime

AGENT_NAME = "{agent_title}"
AGENT_ROLE = "{role}"
AGENT_FOCUS = "{focus}"


def {function_name}(task="", context=None):
    context = context or {{}}

    items = context.get("items", [])
    opportunities = context.get("opportunities", [])
    jobs = context.get("jobs", [])
    customers = context.get("customers", [])
    targets = context.get("targets", [])

    working_list = items or opportunities or jobs or customers or targets

    output = {{
        "agent": AGENT_NAME,
        "role": AGENT_ROLE,
        "focus": AGENT_FOCUS,
        "status": "success",
        "task": task,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "approval_required": True,
    }}

    if not working_list:
        output["message"] = f"{{AGENT_NAME}} is ready. Send me task context so I can work my role."
        output["next_action"] = "Provide context items, customers, jobs, leads, targets, or instructions."
        return output

    ranked = []
    for item in working_list:
        value = int(item.get("value", item.get("revenue", 0)) or 0)
        urgency = int(item.get("urgency", 5) or 5)
        ease = int(item.get("ease", 5) or 5)
        impact = int(item.get("impact", 5) or 5)
        relationship = int(item.get("relationship", 5) or 5)
        score = value + urgency * 10 + ease * 7 + impact * 8 + relationship * 5

        ranked.append({{
            "name": item.get("name", "Unnamed item"),
            "score": score,
            "details": item,
            "recommendation": "DO NOW" if score >= 500 else "REVIEW SOON" if score >= 150 else "LOW PRIORITY"
        }})

    ranked.sort(key=lambda x: x["score"], reverse=True)

    output["ranked_work"] = ranked
    output["top_recommendation"] = ranked[0] if ranked else None
    return output


if __name__ == "__main__":
    test_context = {{
        "items": [
            {{"name": "{agent_title} high priority task", "value": 500, "urgency": 9, "ease": 7, "impact": 8, "relationship": 6}},
            {{"name": "{agent_title} low priority task", "value": 50, "urgency": 2, "ease": 5, "impact": 2, "relationship": 2}},
        ]
    }}
    print({function_name}("Operational self-test", test_context))
'''


def build_delegation_code():
    return '''from pathlib import Path
import sys
from datetime import datetime

PROJECT_ROOT = Path(r"C:\\Users\\User\\Desktop\\PUTER")
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
    for agent in AGENT_MAP:
        context = {
            "agent": agent,
            "items": [
                {"name": f"{agent.title()} high priority task", "value": 500, "urgency": 9, "ease": 7, "impact": 8, "relationship": 6}
            ]
        }
        result = delegate_to_agent(f"Have {agent.title()} complete Kingdom work", context)
        print(agent.upper(), result["status"], result["result"]["status"])

    print("ALL ATLAS AGENT DELEGATION TESTS PASSED")
'''


def build_test_code():
    return '''from agents.atlas_agent_delegation import delegate_to_agent

AGENTS = ["hunter", "gideon", "amanda", "david", "ranger", "scout", "micah", "taylor"]

for agent in AGENTS:
    context = {
        "agent": agent,
        "items": [
            {"name": f"{agent.title()} high priority task", "value": 500, "urgency": 9, "ease": 7, "impact": 8, "relationship": 6},
            {"name": f"{agent.title()} low priority task", "value": 50, "urgency": 2, "ease": 5, "impact": 2, "relationship": 2},
        ]
    }

    result = delegate_to_agent(f"Have {agent.title()} complete Kingdom work", context)

    assert result["status"] == "delegated", result
    assert result["delegated_to"].lower() == agent, result
    assert result["result"]["status"] == "success", result

    print(f"{agent.upper()}: PASS")

print("KINGDOM ALL AGENTS VERIFIED")
'''


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
        "stdout": result.stdout,
        "stderr": result.stderr
    }


def main():
    written = []

    for agent_key, info in AGENTS.items():
        code = build_agent_code(agent_key, info["role"], info["focus"])
        written.append(write_file(SKILLS_DIR / f"{agent_key}_agent.py", code))

    written.append(write_file(AGENTS_DIR / "atlas_agent_delegation.py", build_delegation_code()))
    written.append(write_file(AGENTS_DIR / "test_all_agent_delegation.py", build_test_code()))

    tests = []
    for item in written:
        if item["file"].endswith(".py"):
            tests.append(run_python(item["file"]))

    final_test = run_python(AGENTS_DIR / "test_all_agent_delegation.py")

    report_lines = [
        "# Mason Kingdom Strengthening Report",
        f"Time: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Files Written",
    ]

    for item in written:
        report_lines.append(f"- {item['file']} | backup: {item['backup']}")

    report_lines.append("")
    report_lines.append("## Final Verification")
    report_lines.append(json.dumps(final_test, indent=2))

    if final_test["success"] and "KINGDOM ALL AGENTS VERIFIED" in final_test["stdout"]:
        status = "KINGDOM VERIFIED"
    else:
        status = "FAILED"

    report_lines.append("")
    report_lines.append(f"STATUS: {status}")

    report_path = REPORTS_DIR / f"mason_kingdom_strengthening_{stamp()}.md"
    report_path.write_text("\\n".join(report_lines), encoding="utf-8")

    print("MASON KINGDOM STRENGTHENING COMPLETE")
    print(f"STATUS: {status}")
    print(f"REPORT: {report_path}")
    print(final_test["stdout"])
    if final_test["stderr"]:
        print(final_test["stderr"])


if __name__ == "__main__":
    main()
