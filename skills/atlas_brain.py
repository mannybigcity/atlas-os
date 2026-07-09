import json
from pathlib import Path

from openai import OpenAI
from dotenv import load_dotenv


load_dotenv("config/.env")
client = OpenAI()

KINGDOM_BRAIN_PATH = Path("RAMFAM_KINGDOM_BRAIN")

HUNTER_LEADS_PATH = Path("data") / "hunter_leads.json"
SCOUT_OPPORTUNITIES_PATH = Path("data") / "scout_opportunities.json"
AMANDA_OUTREACH_PATH = Path("data") / "amanda_outreach.json"
PROJECT_STATUS_PATH = Path("data") / "project_statuses.json"


def load_json(path):
    if not path.exists():
        return {}

    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return {}


def list_kingdom_brain_files():
    if not KINGDOM_BRAIN_PATH.exists():
        return []

    return sorted([
        str(file_path.relative_to(KINGDOM_BRAIN_PATH))
        for file_path in KINGDOM_BRAIN_PATH.rglob("*.md")
    ])


def read_kingdom_brain(max_chars=100000):
    if not KINGDOM_BRAIN_PATH.exists():
        return (
            f"KINGDOM BRAIN STATUS: Folder not found.\n"
            f"Expected location: {KINGDOM_BRAIN_PATH.resolve()}"
        )

    markdown_files = sorted(KINGDOM_BRAIN_PATH.rglob("*.md"))

    if not markdown_files:
        return (
            "KINGDOM BRAIN STATUS: Folder found, "
            "but no markdown files were discovered."
        )

    sections = []

    for file_path in markdown_files:
        try:
            content = file_path.read_text(
                encoding="utf-8"
            ).strip()

            relative_path = file_path.relative_to(
                KINGDOM_BRAIN_PATH
            )

            sections.append(
                f"""
=========================
FILE: {relative_path}
=========================

{content}
"""
            )

        except Exception as error:
            sections.append(
                f"""
=========================
FILE: {file_path.name}
=========================

ERROR READING FILE:
{error}
"""
            )

    full_context = "\n".join(sections)

    if len(full_context) > max_chars:
        full_context = (
            full_context[:max_chars]
            + "\n\n[Kingdom Brain truncated due to size.]"
        )

    return full_context


def build_kingdom_snapshot():
    hunter_data = load_json(HUNTER_LEADS_PATH)
    scout_data = load_json(SCOUT_OPPORTUNITIES_PATH)
    amanda_data = load_json(AMANDA_OUTREACH_PATH)
    project_data = load_json(PROJECT_STATUS_PATH)

    hunter_leads = hunter_data.get("leads", [])
    scout_opportunities = scout_data.get("opportunities", [])
    outreach_queue = amanda_data.get("outreach_queue", [])
    projects = project_data.get("projects", [])

    pending_outreach = [
        x for x in outreach_queue
        if x.get("status") == "Pending Contact"
    ]

    active_projects = [
        x for x in projects
        if x.get("status", "").lower() == "building"
    ]

    pipeline_value = 0

    for lead in hunter_leads:
        try:
            pipeline_value += float(
                lead.get("value", 0)
            )
        except Exception:
            pass

    return f"""
RAMFAM KINGDOM SNAPSHOT

Scout Opportunities: {len(scout_opportunities)}
Hunter Leads: {len(hunter_leads)}
Amanda Pending Outreach: {len(pending_outreach)}
Active Projects: {len(active_projects)}
Pipeline Value: ${pipeline_value:,.2f}
"""


def ask_atlas_direct(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are ATLAS the Kingdom Maker, "
                    "Chief of Staff of the RAMFAM Kingdom. "
                    "Use the Kingdom Brain when answering. "
                    "Do not invent information."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    return response.choices[0].message.content


def atlas_kingdom_brain_status():
    files = list_kingdom_brain_files()

    if not KINGDOM_BRAIN_PATH.exists():
        return (
            "KINGDOM BRAIN STATUS: NOT FOUND\n\n"
            f"Expected folder:\n"
            f"{KINGDOM_BRAIN_PATH.resolve()}"
        )

    if not files:
        return (
            "KINGDOM BRAIN STATUS: FOUND BUT EMPTY\n\n"
            f"Folder:\n"
            f"{KINGDOM_BRAIN_PATH.resolve()}\n\n"
            "No .md files found."
        )

    file_list = "\n".join(
        [f"- {file}" for file in files]
    )

    return f"""
KINGDOM BRAIN STATUS: ONLINE

Folder:
{KINGDOM_BRAIN_PATH.resolve()}

Markdown Files Found:
{len(files)}

Files:
{file_list}

Next Step:
Use:
Atlas, consult the Kingdom Brain about [topic]
""".strip()


def atlas_consult_kingdom_brain(question):
    kingdom_brain = read_kingdom_brain(
        max_chars=100000
    )

    prompt = f"""
You are ATLAS the Kingdom Maker.

Answer the King's question using ONLY the
Kingdom Brain Context below.

If the answer is not found in the Kingdom Brain,
respond exactly:

I do not see that documented in the Kingdom Brain yet.

King's Question:
{question}

KINGDOM BRAIN CONTEXT:
{kingdom_brain}
"""

    return ask_atlas_direct(prompt)


def atlas_daily_briefing_ai():
    snapshot = build_kingdom_snapshot()
    kingdom_brain = read_kingdom_brain(
        max_chars=100000
    )

    prompt = f"""
You are ATLAS the Kingdom Maker.

Provide:

1. Kingdom Status
2. Top Priority
3. Orders for Hunter
4. Orders for Amanda
5. Orders for Mason
6. Orders for Micah
7. King's Focus

Keep the response practical,
revenue-focused,
and action-oriented.

{snapshot}

KINGDOM BRAIN CONTEXT:
{kingdom_brain}
"""

    return ask_atlas_direct(prompt)


def atlas_run_the_kingdom_ai():
    snapshot = build_kingdom_snapshot()
    kingdom_brain = read_kingdom_brain(
        max_chars=100000
    )

    prompt = f"""
You are ATLAS the Kingdom Maker.

Tell the King:

- What needs immediate attention
- What revenue action should happen next
- Which agent should work first
- What should NOT be worked on
- Which Kingdom Brain file appears most important

Keep recommendations focused on
revenue,
execution,
and protecting the King's focus.

{snapshot}

KINGDOM BRAIN CONTEXT:
{kingdom_brain}
"""

    return ask_atlas_direct(prompt)


def alfred_daily_briefing_ai():
    return atlas_daily_briefing_ai()


def alfred_run_the_kingdom_ai():
    return atlas_run_the_kingdom_ai()


if __name__ == "__main__":
    print(atlas_daily_briefing_ai())