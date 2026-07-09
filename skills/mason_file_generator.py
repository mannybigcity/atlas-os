from pathlib import Path
import py_compile
from datetime import datetime


PROJECT_ROOT = Path(r"C:\Users\User\Desktop\PUTER")
SKILLS_DIR = PROJECT_ROOT / "skills"


def safe_function_name(agent_name):
    cleaned = agent_name.strip().lower().replace(" ", "_").replace("-", "_")
    return f"{cleaned}_agent"


def build_agent_code(agent_name, role):
    function_name = safe_function_name(agent_name)

    return f'''from datetime import datetime


def {function_name}(task):
    """
    {agent_name} Agent
    Role: {role}
    """

    return {{
        "agent": "{agent_name}",
        "role": "{role}",
        "status": "complete",
        "task": task,
        "result": "{agent_name} received the task and is ready to work.",
        "requires_approval": True,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }}


if __name__ == "__main__":
    print({function_name}("test {agent_name} agent"))
'''


def mason_file_generator(agent_name, role):
    SKILLS_DIR.mkdir(parents=True, exist_ok=True)

    filename = f"{safe_function_name(agent_name)}.py"
    file_path = SKILLS_DIR / filename

    code = build_agent_code(agent_name, role)
    file_path.write_text(code, encoding="utf-8")

    py_compile.compile(str(file_path), doraise=True)

    return {
        "generator": "Mason File Generator",
        "status": "success",
        "agent": agent_name,
        "role": role,
        "file": str(file_path),
        "function": safe_function_name(agent_name),
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }


if __name__ == "__main__":
    print(mason_file_generator("Test", "Disposable test agent"))
