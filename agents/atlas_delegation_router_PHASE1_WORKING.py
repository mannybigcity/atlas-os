import sys
from pathlib import Path

PUTER_ROOT = Path(__file__).resolve().parents[1]

if str(PUTER_ROOT) not in sys.path:
    sys.path.insert(0, str(PUTER_ROOT))

from atlas_hermes_bridge import ask_hermes
from agents.atlas_morning_briefing import generate_morning_briefing


KINGDOM_BRAIN_DIR = PUTER_ROOT / "RAMFAM_KINGDOM_BRAIN"
CONSTITUTION_DIR = KINGDOM_BRAIN_DIR / "Constitution"

CONSTITUTION_FILES = [
    "CONSTITUTION.md",
    "KINGDOM_LAWS.md",
    "KINGDOM_PRIORITY_ORDER.md",
]


def load_constitution() -> str:
    if not CONSTITUTION_DIR.exists():
        return "[CONSTITUTION ERROR] Constitution folder not found."

    sections = []

    for file_name in CONSTITUTION_FILES:
        file_path = CONSTITUTION_DIR / file_name

        if not file_path.exists():
            sections.append(f"\n--- MISSING CONSTITUTION FILE: {file_name} ---\n")
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as error:
            sections.append(
                f"\n--- ERROR READING CONSTITUTION FILE: {file_name} ---\n{error}\n"
            )
            continue

        sections.append(f"\n--- CONSTITUTION FILE: {file_name} ---\n{content}")

    return "[RAMFAM KINGDOM CONSTITUTION]\n" + "\n".join(sections)


def ask_kingdom_brain(question: str) -> str:
    constitution = load_constitution()

    if not KINGDOM_BRAIN_DIR.exists():
        return constitution + "\n\n[KINGDOM BRAIN ERROR] RAMFAM_KINGDOM_BRAIN folder not found."

    question_lower = question.lower()
    matches = []

    for file_path in KINGDOM_BRAIN_DIR.rglob("*.md"):
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            continue

        content_lower = content.lower()

        if any(word in content_lower for word in question_lower.split()):
            matches.append(
                f"\n--- FILE: {file_path.name} ---\n{content[:2500]}"
            )

    if not matches:
        return (
            constitution
            + "\n\n[KINGDOM BRAIN]\n"
            "No direct matching file found, but this question belongs to RAMFAM Kingdom.\n"
            f"Question: {question}"
        )

    return constitution + "\n\n[KINGDOM BRAIN CONTEXT]\n" + "\n".join(matches[:10])


def classify_atlas_request(user_message: str) -> str:
    message = user_message.lower()

    if "morning briefing" in message or "daily briefing" in message:
        return "morning_briefing"

    task_words = [
        "build", "create", "make", "write", "code", "generate",
        "design", "develop", "fix", "upgrade", "system", "importer",
        "plan", "process", "workflow"
    ]

    memory_words = [
        "who is", "what is", "remember", "using what you know",
        "about ramfam", "kingdom", "agent", "hunter", "atlas", "micah",
        "amanda", "gideon", "ranger", "scout", "mason", "hermes",
        "ramfam", "kingdom brain", "constitution", "kingdom laws",
        "priority", "focus", "revenue"
    ]

    has_task = any(word in message for word in task_words)
    has_memory = any(word in message for word in memory_words)

    if has_task and has_memory:
        return "brain_plus_hermes"

    if has_task:
        return "hermes"

    return "kingdom_brain"


def atlas_delegate(user_message: str) -> str:
    route = classify_atlas_request(user_message)

    if route == "morning_briefing":
        return generate_morning_briefing()

    if route == "kingdom_brain":
        return ask_kingdom_brain(user_message)

    if route == "hermes":
        constitution = load_constitution()

        hermes_task = f"""
Atlas is delegating this task to Hermes.

RAMFAM Kingdom Constitution:
{constitution}

User Request:
{user_message}

Hermes, complete the requested task while obeying the RAMFAM Kingdom Constitution.
"""
        return ask_hermes(hermes_task)

    if route == "brain_plus_hermes":
        atlas_context = ask_kingdom_brain(user_message)

        hermes_task = f"""
Atlas is delegating this task to Hermes.

Atlas Context:
{atlas_context}

User Request:
{user_message}

Hermes, use the Atlas context and complete the requested task.
"""
        return ask_hermes(hermes_task)

    return "Atlas could not determine the correct delegation route."


if __name__ == "__main__":
    tests = [
        "Atlas, morning briefing",
        "Atlas, who is Hunter?",
        "Atlas, build a CRM importer.",
        "Atlas, using what you know about RAMFAM Kingdom, build a lead generation system.",
        "Atlas, what should the Kingdom work on next?",
    ]

    for test in tests:
        print("\n==============================")
        print("USER:", test)
        print("ROUTE:", classify_atlas_request(test))
        print("RESPONSE:")
        print(atlas_delegate(test))