from pathlib import Path
import json
import os

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\PUTER")

SAFE_EXTENSIONS = {
    ".py", ".html", ".css", ".js", ".json", ".md", ".txt"
}

IGNORE_FOLDERS = {
    ".git", "__pycache__", "venv", ".venv",
    "node_modules", ".pytest_cache"
}

KINGDOM_ZONES = {
    "agents": "Core agent logic and delegation routes.",
    "skills": "Reusable skills Mason, Atlas, and other agents can call.",
    "brain": "Reasoning, memory, intent, and personality layers.",
    "data": "Live JSON data for missions, leads, statuses, and kingdom state.",
    "memory": "Stored operational memory and approvals.",
    "RAMFAM_KINGDOM_BRAIN": "Long-term knowledge base, laws, playbooks, agent roles, and 99_MEMORY.",
    "logs": "Conversation and activity logs.",
    "crm": "Customer and prospect tracking.",
    "orders": "Order management.",
    "missions": "Mission/task tracking.",
    "ui": "Atlas UI files.",
    "templates": "Flask templates.",
    "sis-website": "SIS Custom Creations website files.",
    "revenue": "Revenue tracking and revenue skills.",
}


def is_safe_file(path: Path) -> bool:
    return path.suffix.lower() in SAFE_EXTENSIONS


def should_ignore(path: Path) -> bool:
    return any(part in IGNORE_FOLDERS for part in path.parts)


def list_safe_files(limit=300):
    files = []

    for root, dirs, filenames in os.walk(PROJECT_ROOT):
        dirs[:] = [d for d in dirs if d not in IGNORE_FOLDERS]

        for filename in filenames:
            path = Path(root) / filename

            if should_ignore(path):
                continue

            if is_safe_file(path):
                files.append(str(path.relative_to(PROJECT_ROOT)))

    return sorted(files)[:limit]


def read_text_file(relative_path, max_chars=4000):
    path = PROJECT_ROOT / relative_path

    if not path.exists():
        return f"[MISSING FILE] {relative_path}"

    if should_ignore(path) or not is_safe_file(path):
        return f"[UNSAFE OR IGNORED FILE] {relative_path}"

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        return text[:max_chars]
    except Exception as error:
        return f"[READ ERROR] {relative_path}: {error}"


def read_json_file(relative_path, max_chars=4000):
    raw = read_text_file(relative_path, max_chars=max_chars)

    try:
        parsed = json.loads(raw)
        pretty = json.dumps(parsed, indent=2)
        return pretty[:max_chars]
    except Exception:
        return raw[:max_chars]


def load_zone_summary():
    summary = []

    for zone, description in KINGDOM_ZONES.items():
        zone_path = PROJECT_ROOT / zone
        exists = zone_path.exists()
        summary.append({
            "zone": zone,
            "description": description,
            "exists": exists,
        })

    return summary


def load_priority_context():
    priority_files = [
        "RAMFAM_KINGDOM_BRAIN/99_MEMORY/ATLAS_HISTORY.md",
        "RAMFAM_KINGDOM_BRAIN/99_MEMORY/PROJECTS.md",
        "RAMFAM_KINGDOM_BRAIN/00_KINGDOM_FOUNDATION/AGENT_ROLES.md",
        "RAMFAM_KINGDOM_BRAIN/00_KINGDOM_FOUNDATION/AGENT_SKILLS.md",
        "RAMFAM_KINGDOM_BRAIN/01_AGENTS_ROLES/MASON.md",
        "RAMFAM_KINGDOM_BRAIN/11_HERMES_ACADEMY/04_AI_AGENTS/HERMES_AGENT_DELEGATION.md",
        "agents/atlas_delegation_router.py",
        "atlas_hermes_bridge.py",
        "skills/mason_hermes_skill.py",
        "skills/mason_skill.py",
        "skills/mason_brain.py",
        "data/kingdom_active_items.json",
        "skills/agent_registry.py",
    ]

    context = {}

    for file in priority_files:
        context[file] = read_text_file(file, max_chars=5000)

    return context


def build_mason_context_package(task=""):
    return {
        "project_root": str(PROJECT_ROOT),
        "task": task,
        "zones": load_zone_summary(),
        "safe_files": list_safe_files(),
        "priority_context": load_priority_context(),
        "rules": {
            "mode": "read_only_context_loader",
            "editing_allowed": False,
            "full_file_replacement_only": True,
            "backup_required_before_edit": True,
            "approval_required_before_edit": True,
            "never_edit": [
                ".env",
                "venv",
                ".venv",
                "__pycache__",
                ".git",
                "node_modules",
            ],
        },
    }


def format_context_for_hermes(task=""):
    package = build_mason_context_package(task)

    lines = []
    lines.append("=== MASON KINGDOM CONTEXT PACKAGE ===")
    lines.append(f"PROJECT ROOT: {package['project_root']}")
    lines.append(f"TASK: {package['task']}")
    lines.append("")

    lines.append("=== KINGDOM ZONES ===")
    for zone in package["zones"]:
        lines.append(f"- {zone['zone']} | exists={zone['exists']} | {zone['description']}")
    lines.append("")

    lines.append("=== SAFE FILE SNAPSHOT ===")
    for file in package["safe_files"][:160]:
        lines.append(f"- {file}")
    lines.append("")

    lines.append("=== PRIORITY CONTEXT ===")
    for file, content in package["priority_context"].items():
        lines.append(f"\n--- FILE: {file} ---")
        lines.append(content)
    lines.append("")

    lines.append("=== MASON RULES ===")
    for key, value in package["rules"].items():
        lines.append(f"{key}: {value}")

    return "\n".join(lines)


if __name__ == "__main__":
    print(format_context_for_hermes("Mason context loader test"))