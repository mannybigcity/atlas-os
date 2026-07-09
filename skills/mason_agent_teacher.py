from pathlib import Path
import subprocess
import sys
from datetime import datetime

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\PUTER")
SKILLS_DIR = PROJECT_ROOT / "skills"
REPORTS_DIR = PROJECT_ROOT / "mason_workspace" / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

AGENTS = {
    "hunter": "Revenue opportunities, lead scoring, and opportunity ranking",
    "gideon": "Finance, profitability, cash flow, and expense awareness",
    "amanda": "Outreach, marketplace messages, partnerships, and quote drafting",
    "david": "CRM, follow-up tracking, customer history, and next actions",
    "ranger": "Customer success, satisfaction, issue handling, and retention",
    "scout": "Research, lead intelligence, market scanning, and opportunity discovery",
    "micah": "Social media posts, captions, content ideas, and engagement strategy",
    "taylor": "Website builder, landing pages, copy blocks, and page improvement plans",
}


def build_agent_file(agent_key, role):
    agent_title = agent_key.title()
    function_name = f"{agent_key}_agent"

    return f'''from datetime import datetime


AGENT_NAME = "{agent_title}"
AGENT_ROLE = "{role}"


def score_item(item):
    value = int(item.get("value", item.get("revenue", 0)) or 0)
    urgency = int(item.get("urgency", 1) or 1)
    ease = int(item.get("ease", 1) or 1)
    relationship = int(item.get("relationship", 1) or 1)
    impact = int(item.get("impact", 1) or 1)

    return value + (urgency * 10) + (ease * 8) + (relationship * 5) + (impact * 7)


def {function_name}(task="", context=None):
    context = context or {{}}
    items = context.get("items", context.get("opportunities", context.get("leads", [])))

    result = {{
        "agent": AGENT_NAME,
        "status": "ready",
        "role": AGENT_ROLE,
        "task": task,
        "message": f"{{AGENT_NAME}} is operational and ready for Kingdom work.",
        "timestamp": datetime.now().isoformat(),
    }}

    if not items:
        result["recommended_next_action"] = "Send me a task plus context items so I can analyze, rank, draft, or recommend next steps."
        return result

    ranked = []
    for item in items:
        name = item.get("name", "Unnamed Item")
        score = score_item(item)
        ranked.append({{
            "name": name,
            "score": score,
            "details": item,
            "recommendation": "Do now" if score >= 100 else "Review soon" if score >= 50 else "Low priority"
        }})

    ranked.sort(key=lambda x: x["score"], reverse=True)

    return {{
        "agent": AGENT_NAME,
        "status": "success",
        "role": AGENT_ROLE,
        "task": task,
        "ranked_items": ranked,
        "top_recommendation": ranked[0] if ranked else None,
        "timestamp": datetime.now().isoformat(),
    }}


if __name__ == "__main__":
    test_context = {{
        "items": [
            {{"name": "High value Kingdom task", "value": 500, "urgency": 9, "ease": 7, "relationship": 5, "impact": 8}},
            {{"name": "Small low urgency task", "value": 50, "urgency": 2, "ease": 5, "relationship": 2, "impact": 2}},
        ]
    }}

    print({function_name}("Phase 2 operational test", test_context))
'''


def main():
    report_lines = []
    report_lines.append("# Mason Agent Teacher Report")
    report_lines.append(f"Generated: {datetime.now().isoformat()}")
    report_lines.append("")

    for agent_key, role in AGENTS.items():
        file_path = SKILLS_DIR / f"{agent_key}_agent.py"
        code = build_agent_file(agent_key, role)

        file_path.write_text(code, encoding="utf-8")

        test = subprocess.run(
            [sys.executable, str(file_path)],
            capture_output=True,
            text=True
        )

        if test.returncode == 0:
            status = "SUCCESS"
        else:
            status = "FAILED"

        report_lines.append(f"## {agent_key.title()}")
        report_lines.append(f"- File: {file_path}")
        report_lines.append(f"- Role: {role}")
        report_lines.append(f"- Test: {status}")
        if test.stdout:
            report_lines.append(f"- Output: {test.stdout[:500]}")
        if test.stderr:
            report_lines.append(f"- Error: {test.stderr[:500]}")
        report_lines.append("")

        print(f"{agent_key.title()}: {status}")

    report_path = REPORTS_DIR / "mason_phase_2_agent_teacher_report.md"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    print("")
    print("MASON PHASE 2 COMPLETE")
    print(f"Report saved to: {report_path}")


if __name__ == "__main__":
    main()
