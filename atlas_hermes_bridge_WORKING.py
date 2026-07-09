import os
import sys
from pathlib import Path


PUTER_ROOT = Path(__file__).resolve().parent

HERMES_ROOT = Path(
    r"C:\Users\User\Desktop\RAMFAM-LAB\Hermes\hermes-agent-main\hermes-agent-main"
)


def load_env_file():
    env_path = PUTER_ROOT / ".env"

    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ[key.strip()] = value.strip().strip('"').strip("'")


def ask_hermes(task: str) -> str:
    """
    Atlas -> Hermes bridge.
    Sends a task to Hermes and returns Hermes' response.
    """

    load_env_file()

    if not HERMES_ROOT.exists():
        return f"HERMES ERROR: Hermes folder not found at {HERMES_ROOT}"

    if str(HERMES_ROOT) not in sys.path:
        sys.path.insert(0, str(HERMES_ROOT))

    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        return "HERMES ERROR: OPENAI_API_KEY is not set."

    try:
        from run_agent import AIAgent

        agent = AIAgent(
            base_url="https://api.openai.com/v1",
            api_key=api_key,
            model="gpt-4o-mini",
            max_iterations=3,
            enabled_toolsets=[],
            disabled_toolsets=["terminal", "browser", "web", "vision"],
            quiet_mode=True,
            api_mode="chat_completions",
            request_overrides={},
        )

        response = agent.chat(task)

        if not response:
            return "HERMES ERROR: Hermes returned no response."

        return response

    except Exception as e:
        return f"HERMES ERROR: {type(e).__name__}: {e}"


def hermes_status() -> str:
    """
    Simple status check for Atlas.
    """
    result = ask_hermes(
        "Hermes bridge status check. Reply with exactly: HERMES READY."
    )
    return result


if __name__ == "__main__":
    print(hermes_status())