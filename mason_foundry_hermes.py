import subprocess
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\PUTER")
HERMES_EXE = Path(r"C:\Users\User\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes.exe")

BRAIN_DIR = PROJECT_ROOT / "RAMFAM_KINGDOM_BRAIN"
SKILLS_DIR = BRAIN_DIR / "03_AGENT_SKILLS"
REPORTS_DIR = BRAIN_DIR / "04_MASON_FOUNDRY"
TEMP_DIR = PROJECT_ROOT / "_mason_temp"

SKILLS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

AGENTS = {
    "Hunter": "Revenue opportunity evaluator, startup cost estimator, ROI analyzer, and business idea filter.",
}

def fallback_skill_file(agent_name, role):
    return f"""# {agent_name} Skill File

## Mission
{agent_name} helps Manny turn ideas into practical action inside RAMFAM KINGDOM.

## Role
{role}

## Inputs Needed
- Task or opportunity description
- Business name if relevant
- Customer or target audience
- Estimated cost
- Estimated revenue
- Deadline or urgency
- Approval status from Manny

## Step By Step Workflow
1. Understand the request.
2. Identify the money-making or time-saving purpose.
3. List required information.
4. Estimate effort, cost, and possible return.
5. Identify risks.
6. Recommend next action.
7. Stop before anything public, financial, or customer-facing unless Manny approves.

## Output Format
- Summary
- Opportunity
- Estimated cost
- Estimated revenue
- Risk level
- Recommended next action
- Approval needed: Yes/No

## Approval Rules
Manny approves anything public, financial, customer-facing, or reputation-impacting.

## Example Tasks
- Evaluate a new side hustle idea.
- Estimate startup cost for a service.
- Compare two revenue opportunities.
- Recommend today’s highest-value action.

## Python Function Design
Function name should be: {agent_name.lower()}_agent(task)

The function should accept a task string and return a dictionary with:
- agent
- status
- summary
- recommendation
- approval_required

## Future Upgrades
- Connect to CRM
- Connect to finance files
- Connect to lead generator
- Connect to daily briefing
"""

def ask_hermes(agent_name, role):
    prompt_file = TEMP_DIR / f"{agent_name.lower()}_hermes_prompt.md"

    prompt_file.write_text(f"""
Create a practical markdown worker skill file for RAMFAM KINGDOM.

Agent: {agent_name}
Role: {role}

Sections:
Mission
What This Agent Does
Inputs Needed
Step By Step Workflow
Output Format
Approval Rules
Example Tasks
Python Function Design
Future Upgrades

Rules:
Manny approves anything public, financial, or customer-facing.
Keep it practical.
Keep it short.
""", encoding="utf-8")

    tiny_prompt = f"Read this file and create the requested skill file: {prompt_file}"

    try:
        result = subprocess.run(
            [str(HERMES_EXE), "-z", tiny_prompt],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=45
        )

        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()

        return fallback_skill_file(agent_name, role)

    except subprocess.TimeoutExpired:
        return fallback_skill_file(agent_name, role)

def main():
    print("MASON FOUNDRY: Safe Hermes extraction starting...")
    print("=" * 60)

    summary_lines = [
        "# Mason Foundry Hermes Report",
        f"Generated: {datetime.now().isoformat()}",
        "",
    ]

    for agent_name, role in AGENTS.items():
        print(f"Building skill file for {agent_name}...")

        content = ask_hermes(agent_name, role)

        skill_file = SKILLS_DIR / f"{agent_name.upper()}_SKILLS.md"
        skill_file.write_text(content, encoding="utf-8")

        summary_lines.append(f"- {agent_name}: created {skill_file}")
        print(f"Saved: {skill_file}")

    report_file = REPORTS_DIR / "MASON_FOUNDRY_HERMES_REPORT.md"
    report_file.write_text("\n".join(summary_lines), encoding="utf-8")

    print("=" * 60)
    print("MASON FOUNDRY SAFE PASS COMPLETE")
    print(f"Report saved to: {report_file}")

if __name__ == "__main__":
    main()