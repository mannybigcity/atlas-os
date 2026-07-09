from pathlib import Path
import json
import re

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\PUTER")
MASON_HERMES_PROFILE = "mason"
MASON_HERMES_SKILL = "mason-profile"
SENSITIVE_CONTEXT_KEY_PARTS = ("api_key", "apikey", "token", "secret", "password")


def task_title(task):
    text = " ".join(str(task or "Mason build task").split())
    return text[:90] or "Mason build task"


def _is_sensitive_key(key):
    normalized = str(key or "").strip().lower().replace("-", "_").replace(" ", "_")
    return any(part in normalized for part in SENSITIVE_CONTEXT_KEY_PARTS)


def redact_sensitive_context(value):
    if isinstance(value, dict):
        redacted = {}
        for key, item in value.items():
            if _is_sensitive_key(key):
                redacted[key] = "[REDACTED]"
            else:
                redacted[key] = redact_sensitive_context(item)
        return redacted
    if isinstance(value, list):
        return [redact_sensitive_context(item) for item in value]
    return value


def build_mason_task_body(task, context, task_id):
    safe_context = redact_sensitive_context(context or {})
    return (
        "Atlas assigned this build/system task to Mason.\n\n"
        f"Task ID: {task_id}\n\n"
        f"Task:\n{task}\n\n"
        "Mason rules:\n"
        "- Preserve Mason identity as Foundry Architect / Kingdom Architect.\n"
        "- Build, test, repair, and report with real verification.\n"
        "- Manny approval is required before public, financial, customer-facing, legal, or reputation-impacting actions.\n"
        "- Do not send messages, publish posts, spend money, contact customers, delete files, or modify secrets.\n\n"
        f"Atlas context:\n{json.dumps(safe_context, indent=2, default=str)}"
    )


def build_create_command(task, context, task_id, project_root=PROJECT_ROOT):
    root = Path(project_root)
    return [
        "hermes",
        "kanban",
        "create",
        task_title(task),
        "--body",
        build_mason_task_body(task, context, task_id),
        "--assignee",
        MASON_HERMES_PROFILE,
        "--workspace",
        f"dir:{root.as_posix()}",
        "--skill",
        MASON_HERMES_SKILL,
        "--created-by",
        "Atlas",
        "--idempotency-key",
        task_id,
        "--json",
    ]


def build_dispatch_command():
    return ["hermes", "kanban", "dispatch", "--max", "1", "--json"]


def parse_kanban_task_id(stdout, fallback_task_id):
    text = stdout or ""
    try:
        payload = json.loads(text)
        if isinstance(payload, dict):
            return payload.get("id") or payload.get("task_id") or fallback_task_id
    except Exception:
        pass

    match = re.search(r"\bt_[0-9a-fA-F]+\b", text)
    if match:
        return match.group(0)

    for line in text.splitlines():
        line = line.strip()
        if line.startswith("t") and line[1:].isdigit():
            return line
    return fallback_task_id
