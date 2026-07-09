import os
import subprocess

DEFAULT_TIMEOUT_SECONDS = int(os.getenv("ATLAS_HERMES_TIMEOUT_SECONDS", "600"))
MAX_PROMPT_CHARS = int(os.getenv("ATLAS_HERMES_MAX_PROMPT_CHARS", "5500"))


def _trim_prompt(prompt: str) -> str:
    prompt = str(prompt or "").strip()
    if len(prompt) > MAX_PROMPT_CHARS:
        return prompt[:MAX_PROMPT_CHARS] + "\n\n[TRIMMED BY ATLAS HERMES BRIDGE FOR COMMAND SAFETY]"
    return prompt


def _clean_hermes_output(output: str) -> str:
    lines = []
    for line in (output or "").splitlines():
        if line.strip().lower().startswith("session_id:"):
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def ask_hermes(prompt: str) -> str:
    """Send an ATLAS UI message to the Hermes atlas profile.

    This is the bridge that lets the ATLAS web UI use Hermes as the engine
    while keeping ATLAS as Manny's front door.
    """
    prompt = _trim_prompt(prompt)
    if not prompt:
        return "ATLAS needs a message before Hermes can respond."

    command = ["hermes", "--profile", "atlas", "chat", "-Q", "-q", prompt]

    try:
        result = subprocess.run(
            command,
            cwd=r"C:\Users\User\Desktop\PUTER",
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=DEFAULT_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return "Hermes Atlas bridge failed: the atlas profile timed out before returning a response."
    except Exception as error:
        return f"Hermes Atlas bridge failed: {error}"

    output = _clean_hermes_output(result.stdout or "")
    errors = _clean_hermes_output(result.stderr or "")

    if result.returncode != 0:
        detail = errors or output or f"Hermes exited with code {result.returncode}."
        return f"Hermes Atlas bridge failed: {detail}"

    if errors:
        return (output + "\n\n[HERMES WARNINGS]\n" + errors).strip()

    return output or "Hermes Atlas bridge returned no text."
