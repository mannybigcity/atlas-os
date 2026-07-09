import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\PUTER")
BRAIN_DIR = PROJECT_ROOT / "RAMFAM_KINGDOM_BRAIN"
SKILLS_MD_DIR = BRAIN_DIR / "03_AGENT_SKILLS"
FOUNDRY_DIR = BRAIN_DIR / "04_MASON_FOUNDRY"
PY_SKILLS_DIR = PROJECT_ROOT / "skills"

REGISTRY_DIR = BRAIN_DIR / "05_AGENT_REGISTRY"
REGISTRY_JSON = REGISTRY_DIR / "agent_registry_v2.json"
REGISTRY_MD = REGISTRY_DIR / "AGENT_REGISTRY_V2.md"

REGISTRY_DIR.mkdir(parents=True, exist_ok=True)


AGENT_PROFILES = {
    "Atlas": {
        "title": "Kingdom Chief of Staff",
        "mascot": "Golden Lion",
        "room": "Throne Room",
        "authority": "Chief of Staff",
        "reports_to": "Manny",
        "overrides_atlas": False,
        "approval_required": True
    },
    "Mason": {
        "title": "Foundry Architect",
        "mascot": "Beaver",
        "room": "Mason Workshop",
        "authority": "Builder",
        "reports_to": "Atlas",
        "overrides_atlas": False,
        "approval_required": False
    },
    "Hunter": {
        "title": "Revenue Commander",
        "mascot": "Bald Eagle",
        "room": "Hunter War Room",
        "authority": "Opportunity Scout",
        "reports_to": "Atlas",
        "overrides_atlas": False,
        "approval_required": True
    },
    "Scout": {
        "title": "Research Agent",
        "mascot": "Red-Tailed Hawk",
        "room": "Scout Tower",
        "authority": "Research",
        "reports_to": "Atlas",
        "overrides_atlas": False,
        "approval_required": True
    },
    "Amanda": {
        "title": "Outreach and Marketplace Agent",
        "mascot": "Panda",
        "room": "Amanda Marketplace",
        "authority": "Drafting Only",
        "reports_to": "Atlas",
        "overrides_atlas": False,
        "approval_required": True
    },
    "David": {
        "title": "CRM Agent",
        "mascot": "Wolf",
        "room": "CRM Dashboard",
        "authority": "Organizer",
        "reports_to": "Atlas",
        "overrides_atlas": False,
        "approval_required": False
    },
    "Gideon": {
        "title": "Finance Agent",
        "mascot": "Bull",
        "room": "Gideon Finance Office",
        "authority": "Financial Review",
        "reports_to": "Atlas",
        "overrides_atlas": False,
        "approval_required": True
    },
    "Ranger": {
        "title": "Customer Success Agent",
        "mascot": "German Shepherd",
        "room": "Ranger Customer Success Center",
        "authority": "Customer Care Drafting",
        "reports_to": "Atlas",
        "overrides_atlas": False,
        "approval_required": True
    },
    "Micah": {
        "title": "Social Media Agent",
        "mascot": "Fox",
        "room": "Micah Media Studio",
        "authority": "Drafting Only",
        "reports_to": "Atlas",
        "overrides_atlas": False,
        "approval_required": True
    },
    "Taylor": {
        "title": "Website Builder Agent",
        "mascot": "Tiger",
        "room": "Taylor Web Studio",
        "authority": "Website Drafting",
        "reports_to": "Atlas",
        "overrides_atlas": False,
        "approval_required": True
    },
    "Oracle": {
        "title": "Kingdom Intelligence and Trend Watchtower",
        "mascot": "Owl",
        "room": "Oracle Watchtower",
        "authority": "Trend Intelligence",
        "reports_to": "Atlas",
        "overrides_atlas": False,
        "approval_required": False
    },
    "Lucky": {
        "title": "Kingdom DJ and Atmosphere Director",
        "mascot": "DJ",
        "room": "Lucky Sound Booth",
        "authority": "Atmosphere Direction",
        "reports_to": "Atlas",
        "overrides_atlas": False,
        "approval_required": True
    },
    "Solomon": {
        "title": "Kingdom Wisdom Advisor",
        "mascot": "Grey and White Maned Wise Lion",
        "room": "Solomon Council Chamber",
        "authority": "Senior Advisor",
        "reports_to": "Atlas",
        "overrides_atlas": False,
        "approval_required": False
    }
}


AGENT_ASSIGNED_SKILLS = {
    "Hunter": ["ETSY_RESEARCH_V1"],
    "Oracle": ["ETSY_RESEARCH_V1"],
    "Amanda": ["ETSY_RESEARCH_V1"],
}

def safe_name(agent_name):
    return agent_name.strip().lower().replace(" ", "_")


def read_text_if_exists(path):
    if path.exists():
        return path.read_text(encoding="utf-8", errors="replace")
    return ""


def test_python_worker(worker_file):
    if not worker_file.exists():
        return {
            "status": "missing",
            "returncode": None,
            "stdout": "",
            "stderr": "Worker file missing."
        }

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
            "status": "passed" if result.returncode == 0 and result.stdout.strip() else "failed",
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip()
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "returncode": 999,
            "stdout": "",
            "stderr": "Worker test timed out."
        }


def load_build_report(agent_name):
    report_file = FOUNDRY_DIR / f"{agent_name.upper()}_BUILD_REPORT.json"
    if not report_file.exists():
        return None

    try:
        return json.loads(report_file.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None


def build_registry():
    registry = {
        "registry_name": "RAMFAM KINGDOM Agent Registry v2",
        "generated_at": datetime.now().isoformat(),
        "project_root": str(PROJECT_ROOT),
        "total_agents": len(AGENT_PROFILES),
        "agents": []
    }

    for agent_name, profile in AGENT_PROFILES.items():
        agent_safe = safe_name(agent_name)

        skill_file = SKILLS_MD_DIR / f"{agent_name.upper()}_SKILLS.md"
        worker_file = PY_SKILLS_DIR / f"{agent_safe}_agent.py"
        build_report_file = FOUNDRY_DIR / f"{agent_name.upper()}_BUILD_REPORT.json"

        skill_exists = skill_file.exists()
        worker_exists = worker_file.exists()
        report_exists = build_report_file.exists()

        test_result = test_python_worker(worker_file)
        build_report = load_build_report(agent_name)

        if worker_exists and test_result["status"] == "passed":
            status = "ACTIVE"
        elif worker_exists:
            status = "NEEDS_REPAIR"
        elif skill_exists:
            status = "READY_TO_FORGE"
        else:
            status = "MISSING_SKILL_FILE"

        registry["agents"].append({
            "name": agent_name,
            "title": profile["title"],
            "mascot": profile["mascot"],
            "room": profile["room"],
            "authority": profile["authority"],
            "reports_to": profile["reports_to"],
            "overrides_atlas": profile["overrides_atlas"],
            "approval_required": profile["approval_required"],
            "assigned_skills": AGENT_ASSIGNED_SKILLS.get(agent_name, []),
            "status": status,
            "skill_file": str(skill_file),
            "skill_exists": skill_exists,
            "worker_file": str(worker_file),
            "worker_exists": worker_exists,
            "build_report_file": str(build_report_file),
            "build_report_exists": report_exists,
            "last_build_source": build_report.get("source") if build_report else None,
            "last_test_status": test_result["status"],
            "last_test_stdout": test_result["stdout"],
            "last_test_stderr": test_result["stderr"]
        })

    return registry


def write_markdown(registry):
    active_count = sum(1 for agent in registry["agents"] if agent["status"] == "ACTIVE")

    lines = []
    lines.append("# RAMFAM KINGDOM Agent Registry v2")
    lines.append("")
    lines.append(f"Generated: {registry['generated_at']}")
    lines.append(f"Project Root: `{registry['project_root']}`")
    lines.append("")
    lines.append(f"Total Agents: {registry['total_agents']}")
    lines.append(f"Active Agents: {active_count}")
    lines.append("")
    lines.append("## Authority Rule")
    lines.append("")
    lines.append("Manny is final human authority.")
    lines.append("Atlas is Chief of Staff.")
    lines.append("Solomon advises Atlas but does not override Atlas.")
    lines.append("No agent overrides Atlas.")
    lines.append("Public, financial, legal, customer-facing, or reputation-impacting actions require Manny approval.")
    lines.append("")
    lines.append("## Agents")
    lines.append("")
    lines.append("| Agent | Title | Mascot | Room | Reports To | Status | Approval Required |")
    lines.append("|---|---|---|---|---|---|---|")

    for agent in registry["agents"]:
        lines.append(
            f"| {agent['name']} | {agent['title']} | {agent['mascot']} | {agent['room']} | "
            f"{agent['reports_to']} | {agent['status']} | {agent['approval_required']} |"
        )

    lines.append("")
    lines.append("## Build Details")
    lines.append("")

    for agent in registry["agents"]:
        lines.append(f"### {agent['name']}")
        lines.append("")
        lines.append(f"- Title: {agent['title']}")
        lines.append(f"- Mascot: {agent['mascot']}")
        lines.append(f"- Room: {agent['room']}")
        lines.append(f"- Authority: {agent['authority']}")
        lines.append(f"- Reports To: {agent['reports_to']}")
        lines.append(f"- Overrides Atlas: {agent['overrides_atlas']}")
        lines.append(f"- Approval Required: {agent['approval_required']}")
        lines.append(f"- Assigned Skills: {', '.join(agent['assigned_skills']) if agent['assigned_skills'] else 'None'}")
        lines.append(f"- Status: {agent['status']}")
        lines.append(f"- Skill File Exists: {agent['skill_exists']}")
        lines.append(f"- Worker File Exists: {agent['worker_exists']}")
        lines.append(f"- Build Report Exists: {agent['build_report_exists']}")
        lines.append(f"- Last Build Source: {agent['last_build_source']}")
        lines.append(f"- Last Test Status: {agent['last_test_status']}")
        lines.append("")

    REGISTRY_MD.write_text("\n".join(lines), encoding="utf-8")


def main():
    registry = build_registry()

    REGISTRY_JSON.write_text(json.dumps(registry, indent=2), encoding="utf-8")
    write_markdown(registry)

    active_count = sum(1 for agent in registry["agents"] if agent["status"] == "ACTIVE")

    print("RAMFAM KINGDOM Agent Registry v2 complete.")
    print(f"Total agents: {registry['total_agents']}")
    print(f"Active agents: {active_count}")
    print(f"JSON: {REGISTRY_JSON}")
    print(f"Markdown: {REGISTRY_MD}")
    print("")
    print("Agent Status:")
    for agent in registry["agents"]:
        print(f"- {agent['name']}: {agent['status']}")


if __name__ == "__main__":
    main()