import json
import re
import sys
from pathlib import Path

PUTER_ROOT = Path(__file__).resolve().parents[1]

if str(PUTER_ROOT) not in sys.path:
    sys.path.insert(0, str(PUTER_ROOT))

from atlas_hermes_bridge import ask_hermes
from agents.atlas_morning_briefing import generate_morning_briefing
from skills.mason_today_plan import mason_today_plan
from skills.mason_chat import mason_chat
from skills.mason_advisor import mason_advisor
from skills.atlas_strategic_command import atlas_strategic_command


KINGDOM_BRAIN_DIR = PUTER_ROOT / "RAMFAM_KINGDOM_BRAIN"
CONSTITUTION_DIR = KINGDOM_BRAIN_DIR / "Constitution"

CONSTITUTION_FILES = [
    "CONSTITUTION.md",
    "KINGDOM_LAWS.md",
    "KINGDOM_PRIORITY_ORDER.md",
]

STOP_WORDS = {
    "atlas", "alfred", "puter",
    "who", "what", "where", "when", "why", "how",
    "is", "are", "am", "be", "being", "been", "does", "do", "did",
    "the", "a", "an", "and", "or", "to", "of", "for", "in", "on", "with",
    "about", "consult", "search", "find", "tell", "me", "show", "know", "remember", "recall",
    "you", "your", "yours", "my", "mine", "our", "we", "us",
    "kingdom", "brain", "ramfam", "please", "read", "file",
}

BROAD_MEMORY_PHRASES = (
    "what do you remember",
    "what do you know about me",
    "tell me about me",
    "who am i",
    "why does atlas exist",
    "why atlas exists",
)


def normalize_memory_word(word: str) -> str:
    word = word.lower().strip()
    if len(word) > 3 and word.endswith("s"):
        return word[:-1]
    return word


def memory_tokens(text: str) -> set[str]:
    return {normalize_memory_word(word) for word in re.findall(r"[A-Za-z0-9]+", text.lower())}


def clean_question_words(question: str) -> list[str]:
    words = re.findall(r"[A-Za-z0-9]+", question.lower())
    return [normalize_memory_word(word) for word in words if word not in STOP_WORDS and len(word) > 1]


def is_broad_memory_request(question: str, question_words: list[str]) -> bool:
    message = question.lower()
    return not question_words or any(phrase in message for phrase in BROAD_MEMORY_PHRASES)


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
            sections.append(f"\n--- ERROR READING {file_name} ---\n{error}\n")
            continue

        sections.append(f"\n--- {file_name} ---\n{content}")

    return "\n".join(sections)


def read_kingdom_file(user_message: str) -> str:
    message = user_message.replace("\\", "/")

    # Direct full path support
    full_path_match = re.search(r"([A-Za-z]:/[^:\n\r]+?\.(md|txt|json|py|html|css|js))", message)
    if full_path_match:
        file_path = Path(full_path_match.group(1))
    else:
        # Filename support, example: TAYLOR.md
        file_match = re.search(r"([A-Za-z0-9_\-]+\.(md|txt|json|py|html|css|js))", user_message)
        if not file_match:
            return "Atlas: Tell me the exact file name or full path to read."

        target_name = file_match.group(1).strip()
        matches = list(KINGDOM_BRAIN_DIR.rglob(target_name))

        if not matches:
            return f"Atlas: I could not find `{target_name}` inside RAMFAM_KINGDOM_BRAIN."

        file_path = matches[0]

    if not file_path.exists():
        return f"Atlas: File not found:\n{file_path}"

    try:
        lines = file_path.read_text(encoding="utf-8").splitlines()
    except Exception as error:
        return f"Atlas: Error reading file:\n{error}"

    content = "\n".join(lines)

    return (
        f"Atlas: Full file read successfully.\n\n"
        f"Path: {file_path}\n"
        f"Lines read: {len(lines)}\n\n"
        f"{content}"
    )


def _flatten_memory_json(value, prefix="") -> list[str]:
    """Convert structured JSON memory into searchable, readable fact lines."""
    lines = []

    if isinstance(value, dict):
        for key, child in value.items():
            clean_key = str(key).replace("_", " ")
            child_prefix = f"{prefix}.{clean_key}" if prefix else clean_key
            lines.extend(_flatten_memory_json(child, child_prefix))
        return lines

    if isinstance(value, list):
        for index, child in enumerate(value, start=1):
            child_prefix = f"{prefix} {index}" if prefix else str(index)
            lines.extend(_flatten_memory_json(child, child_prefix))
        return lines

    if prefix:
        lines.append(f"- {prefix}: {value}")
    else:
        lines.append(f"- {value}")
    return lines


def read_memory_file_lines(file_path: Path) -> list[str]:
    """Read supported 99_MEMORY source files into clean searchable lines."""
    content = file_path.read_text(encoding="utf-8-sig")
    if file_path.suffix.lower() == ".json":
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            return [line.strip() for line in content.splitlines() if line.strip()]
        return _flatten_memory_json(parsed)
    return [line.strip() for line in content.splitlines() if line.strip()]


def iter_memory_files(memory_dir: Path):
    """Yield all supported Atlas memory files, not only markdown summaries."""
    for suffix in ("*.md", "*.txt", "*.json"):
        yield from memory_dir.rglob(suffix)


def ask_kingdom_brain(question: str) -> str:
    memory_dir = KINGDOM_BRAIN_DIR / "99_MEMORY"

    if not memory_dir.exists():
        return "Atlas: 99_MEMORY folder not found."

    question_words = clean_question_words(question)
    broad_memory_request = is_broad_memory_request(question, question_words)
    matches = []

    for file_path in iter_memory_files(memory_dir):
        try:
            lines = read_memory_file_lines(file_path)
        except Exception:
            continue

        content = "\n".join(lines)
        source_tokens = memory_tokens(f"{file_path.name} {content}")
        query_tokens = set(question_words)
        score = len(query_tokens & source_tokens)

        if broad_memory_request and file_path.name == "ATLAS_PERSONAL_MEMORY_SUMMARY.md":
            matches.append(
                (
                    100,
                    f"--- MEMORY SOURCE: {file_path.relative_to(KINGDOM_BRAIN_DIR)} ---\n"
                    f"{chr(10).join(lines[:20])}"
                )
            )
            continue

        if score <= 0:
            continue

        relevant = []
        for line in lines:
            if query_tokens & memory_tokens(line):
                relevant.append(line)

        excerpt = "\n".join(relevant[:10]) if relevant else "\n".join(lines[:10])
        matches.append(
            (
                score,
                f"--- MEMORY SOURCE: {file_path.relative_to(KINGDOM_BRAIN_DIR)} ---\n"
                f"{excerpt}"
            )
        )

    if not matches:
        return "Atlas: I searched 99_MEMORY first but did not find a direct memory match."

    ordered_matches = [entry for _, entry in sorted(matches, key=lambda item: item[0], reverse=True)]
    return "Atlas consulted 99_MEMORY first:\n\n" + "\n\n".join(ordered_matches[:3])

def classify_atlas_request(user_message: str) -> str:
    message = user_message.lower()

    if "read" in message and (".md" in message or ".txt" in message or ".json" in message or ".py" in message):
        return "read_file"

    if "constitution" in message or "kingdom laws" in message:
        return "constitution"

    if "morning briefing" in message or "daily briefing" in message:
        return "morning_briefing"

    memory_questions = [
        "what do you remember",
        "do you remember",
        "what do you know about",
        "who is",
        "who am i",
        "tell me about",
        "remember about",
        "why does atlas exist",
        "why atlas exists",
        "family",
        "wife",
        "deleana",
        "daija",
        "myles",
        "daughter",
        "son",
        "granddaughter",
        "dezarai",
        "nickname",
        "birthday",
        "current goal",
        "sis believe",
        "every project tells",
    ]

    if any(phrase in message for phrase in memory_questions):
        return "kingdom_brain"

    if (
        "what should we work on today" in message
        or "biggest bottleneck" in message
        or "highest roi" in message
        or "where should we focus" in message
    ):
        return "atlas_strategic_command"

    if "mason" in message and (
        "focus on today" in message
        or "focus today" in message
        or "what should we focus on" in message
        or "advisor" in message
        or "advice" in message
    ):
        return "mason_advisor"

    if "mason" in message and (
        "call" in message
        or "talk" in message
        or "ask" in message
        or "what does mason" in message
        or "mason got going on" in message
    ):
        return "mason_chat"

    if "mason" in message and (
        "plan" in message
        or "builder" in message
        or "today" in message
        or "build mode" in message
        or "what should we build" in message
    ):
        return "mason_today_plan"

    task_words = [
        "build", "create", "make", "write", "code", "generate",
        "design", "develop", "fix", "upgrade", "system", "importer",
        "plan", "process", "workflow", "strategy", "recommend",
    ]

    if any(word in message for word in task_words):
        return "hermes"

    return "hermes"


def atlas_delegate(user_message: str) -> str:
    route = classify_atlas_request(user_message)

    if route == "read_file":
        return read_kingdom_file(user_message)

    if route == "constitution":
        return load_constitution()

    if route == "morning_briefing":
        return generate_morning_briefing()

    if route == "atlas_strategic_command":
        return atlas_strategic_command(user_message)

    if route == "mason_chat":
        return mason_chat(user_message)

    if route == "mason_advisor":
        return mason_advisor()

    if route == "mason_today_plan":
        return mason_today_plan()

    if route == "kingdom_brain":
        return ask_kingdom_brain(user_message)

    if route == "hermes":
        hermes_task = f"""
Atlas is delegating this task to Hermes.

Manny's Request:
{user_message}

Keep the response concise.
Do not print the Constitution unless Manny specifically asks for it.
"""
        return ask_hermes(hermes_task)

    return "Atlas could not determine the correct route."



