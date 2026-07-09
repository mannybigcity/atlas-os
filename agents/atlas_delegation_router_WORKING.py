import sys
from pathlib import Path

PUTER_ROOT = Path(__file__).resolve().parents[1]

if str(PUTER_ROOT) not in sys.path:
    sys.path.insert(0, str(PUTER_ROOT))

from atlas_hermes_bridge import ask_hermes


KINGDOM_BRAIN_DIR = PUTER_ROOT / "RAMFAM_KINGDOM_BRAIN"


def ask_kingdom_brain(question: str) -> str:
    """
    Reads RAMFAM Kingdom Brain markdown files and returns matching context.
    """

    if not KINGDOM_BRAIN_DIR.exists():
        return "[KINGDOM BRAIN ERROR] kingdom_brain folder not found."

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
            "[KINGDOM BRAIN]\n"
            "No direct matching file found, but this question belongs to RAMFAM Kingdom.\n"
            f"Question: {question}"
        )

    return "[KINGDOM BRAIN CONTEXT]\n" + "\n".join(matches[:5])


def classify_atlas_request(user_message: str) -> str:
    message = user_message.lower()

    task_words = [
        "build", "create", "make", "write", "code", "generate",
        "design", "develop", "fix", "upgrade", "system", "importer",
        "plan", "process", "workflow"
    ]

    memory_words = [
        "who is", "what is", "remember", "using what you know",
        "about ramfam", "kingdom", "agent", "hunter", "atlas", "micah",
        "amanda", "gideon", "ranger", "scout", "mason", "hermes",
        "ramfam", "kingdom brain"
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

    if route == "kingdom_brain":
        return ask_kingdom_brain(user_message)

    if route == "hermes":
        return ask_hermes(user_message)

    if route == "brain_plus_hermes":
        brain_context = ask_kingdom_brain(user_message)

        hermes_task = f"""
Atlas is delegating this task to Hermes.

Kingdom Brain Context:
{brain_context}

User Request:
{user_message}

Hermes, use the Kingdom context and complete the requested task.
"""
        return ask_hermes(hermes_task)

    return "Atlas could not determine the correct delegation route."


if __name__ == "__main__":
    tests = [
        "Atlas, who is Hunter?",
        "Atlas, build a CRM importer.",
        "Atlas, using what you know about RAMFAM Kingdom, build a lead generation system."
    ]

    for test in tests:
        print("\n==============================")
        print("USER:", test)
        print("ROUTE:", classify_atlas_request(test))
        print("RESPONSE:")
        print(atlas_delegate(test))