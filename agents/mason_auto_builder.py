import json
import subprocess
from datetime import datetime
from pathlib import Path

from agents.mason_hermes_skill_router import choose_skill, build_safe_preview_command
try:
    from skills.mason_hermes_skill import mason_ask_hermes
except Exception:
    def mason_ask_hermes(task_text: str) -> str:
        return try_hermes_skill_preview(task_text)


PROJECT_ROOT = Path(r"C:\Users\User\Desktop\PUTER")
AGENTS_DIR = PROJECT_ROOT / "agents"
SKILLS_DIR = PROJECT_ROOT / "skills"
WORKSPACE = PROJECT_ROOT / "mason_workspace"
CURRENT_TASK_FILE = WORKSPACE / "current_mason_task.md"
REPORTS_DIR = WORKSPACE / "reports"


def safe_read(path: Path, limit: int = 4000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:limit]
    except Exception as e:
        return f"[Could not read {path}: {e}]"


def inspect_kingdom_files() -> dict:
    agent_files = sorted([p.name for p in AGENTS_DIR.glob("*.py")]) if AGENTS_DIR.exists() else []
    skill_files = sorted([p.name for p in SKILLS_DIR.glob("*.py")]) if SKILLS_DIR.exists() else []

    important_files = {}
    for rel in [
        "agents/assistant.py",
        "agents/atlas_delegation_router.py",
        "agents/mason_auto_builder.py",
        "agents/mason_hermes_skill_router.py",
        "skills/agent_registry.py",
        "skills/assign_agent_task.py",
        "skills/mason_auto_builder_skill.py",
    ]:
        path = PROJECT_ROOT / rel
        if path.exists():
            important_files[rel] = safe_read(path)

    return {
        "agent_files": agent_files,
        "skill_files": skill_files,
        "important_files": important_files,
    }


def write_mason_task_file(task_text: str, skill_name: str) -> None:
    WORKSPACE.mkdir(exist_ok=True)

    CURRENT_TASK_FILE.write_text(
        f"""# Mason Auto-Builder Task

## User Task
{task_text}

## Routed Hermes Skill
{skill_name}

## Rule
Do not send giant prompts to Hermes.
Use local files, small task descriptions, and Hermes skills only.

## Status
Prepared for Mason Auto-Builder.
""",
        encoding="utf-8",
    )


def write_architecture_report(task_text: str, route, inspection: dict) -> str:
    REPORTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = REPORTS_DIR / f"mason_kingdom_inspection_{timestamp}.md"

    agent_names = ["amanda", "david", "gideon", "hunter", "micah", "ranger", "scout", "taylor"]

    found_agents = []
    missing_agents = []

    all_files_lower = " ".join(inspection["agent_files"] + inspection["skill_files"]).lower()

    for name in agent_names:
        if name in all_files_lower:
            found_agents.append(name)
        else:
            missing_agents.append(name)

    report_file.write_text(
        f"""# Mason Kingdom Inspection Report

## Time
{datetime.now()}

## User Task
{task_text}

## Routed Intent
{route.intent}

## Routed Hermes Skill
{route.hermes_skill}

## Agent Files Found
{json.dumps(inspection["agent_files"], indent=2)}

## Skill Files Found
{json.dumps(inspection["skill_files"], indent=2)}

## Named Kingdom Agents Detected
{json.dumps(found_agents, indent=2)}

## Named Kingdom Agents Missing Dedicated Files
{json.dumps(missing_agents, indent=2)}

## Mason Recommendation
Mason should build the agents in this order:

1. David — CRM foundation because follow-ups, prospects, and customer records feed everything.
2. Gideon — finance/revenue reporting because money decisions guide the day.
3. Hunter — revenue commander because he needs David and Gideon data.
4. Amanda — outreach/marketplace because she needs prospects and offer data.
5. Micah — social/content because he needs offers and campaigns.
6. Ranger — customer success because orders and follow-ups must be protected.
7. Scout — opportunity scout because he feeds Hunter/Amanda.
8. Taylor — website tailor because he can use all previous business intelligence.

## Safe Build Plan
- Do not modify assistant.py yet.
- Create one agent skill file at a time inside skills/.
- Each new file should expose one simple function.
- Each function should return a useful text report first.
- After each file is created, run py_compile.
- Only after each agent works alone should ATLAS tools be updated.

## Next Recommended File
C:\\Users\\User\\Desktop\\PUTER\\skills\\david_crm_agent.py

## Proof of Local Autonomy
Mason inspected local project folders directly and produced this report without sending a giant prompt to Hermes.
""",
        encoding="utf-8",
    )

    return str(report_file)


def try_hermes_skill_preview(task_text: str) -> str:
    preview_command = build_safe_preview_command(task_text)

    try:
        result = subprocess.run(
            preview_command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=8,
        )
        return result.stdout or result.stderr or "[Hermes returned no output]"
    except subprocess.TimeoutExpired:
        return "[Hermes skill preview timed out. Mason continued using local inspection.]"
    except Exception as e:
        return f"[Hermes skill preview failed: {e}]"


def run_mason_auto_builder(task_text: str) -> str:
    route = choose_skill(task_text)
    write_mason_task_file(task_text, route.hermes_skill)

    inspection = inspect_kingdom_files()
    report_path = write_architecture_report(task_text, route, inspection)
    hermes_preview = try_hermes_skill_preview(task_text)

    return (
        f"MASON AUTO-BUILDER RAN\n"
        f"Task file: {CURRENT_TASK_FILE}\n"
        f"Intent: {route.intent}\n"
        f"Hermes skill: {route.hermes_skill}\n"
        f"Architecture report: {report_path}\n\n"
        f"HERMES PREVIEW STATUS:\n"
        f"{hermes_preview[:1500]}"
    )


def mason_plan_builder_task(task_text: str) -> dict:
    """Create safety backups, run a Python syntax check, then ask Hermes for a plan."""
    project_root = Path(PROJECT_ROOT)
    checked_rel_paths = ["agents/mason_auto_builder.py", "skills/mason_skill.py"]
    checked_files = [rel for rel in checked_rel_paths if (project_root / rel).exists()]

    backup_directory = project_root / "mason_workspace" / "backups" / datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_directory.mkdir(parents=True, exist_ok=True)

    backups_created = []
    for rel in checked_files:
        source = project_root / rel
        destination = backup_directory / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(source.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
        backups_created.append({"file": rel, "backup_path": str(destination)})

    command = ["python", "-m", "py_compile", *checked_files]
    if checked_files:
        check_result = subprocess.run(
            command,
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        passed = check_result.returncode == 0
        output = (check_result.stdout or "") + (check_result.stderr or "")
    else:
        passed = False
        output = "No Mason files found to check."

    python_check = {
        "passed": passed,
        "command": " ".join(command),
        "checked_files": checked_files,
        "output": output,
    }

    if not passed:
        return {
            "status": "failed python check before Hermes planning",
            "backup_directory": str(backup_directory),
            "backups_created": backups_created,
            "python_check": python_check,
            "hermes_plan": None,
        }

    hermes_plan = mason_ask_hermes(task_text)
    return {
        "status": "planned",
        "backup_directory": str(backup_directory),
        "backups_created": backups_created,
        "python_check": python_check,
        "hermes_plan": hermes_plan,
    }


if __name__ == "__main__":
    import sys

    task = " ".join(sys.argv[1:]) or "inspect RAMFAM KINGDOM architecture"
    print(run_mason_auto_builder(task))
