import os
from pathlib import Path
from openai import OpenAI

PUTER_ROOT = Path(__file__).resolve().parents[1]
PERSONA_FILE = PUTER_ROOT / "agents" / "personas" / "mason_persona.md"
ENV_FILE = PUTER_ROOT / ".env"


def load_env_file():
    if not ENV_FILE.exists():
        return

    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ[key.strip()] = value.strip().strip('"').strip("'")


def load_mason_persona():
    if not PERSONA_FILE.exists():
        return "Mason persona file not found."

    return PERSONA_FILE.read_text(encoding="utf-8")


def mason_chat(user_message):
    load_env_file()

    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        return "MASON ERROR: OPENAI_API_KEY is not set."

    persona = load_mason_persona()
    client = OpenAI(api_key=api_key)

    clean_message = user_message.replace("Atlas,", "").replace("atlas,", "").strip()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": f"""
You are MASON, not Atlas.

You are inside RAMFAM KINGDOM.
Atlas is only the router who called you into the meeting room.

Always respond as Mason.
Always start your response with: 🦫 MASON:

{persona}

Keep responses short, practical, builder-minded, and direct.
"""
            },
            {
                "role": "user",
                "content": clean_message
            }
        ],
        temperature=0.7,
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    print(mason_chat("Atlas, call Mason"))