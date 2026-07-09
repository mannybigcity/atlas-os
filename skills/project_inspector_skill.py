import json
from pathlib import Path


REQUIREMENTS_PATH = Path("data") / "project_requirements.json"


def load_requirements():
    if not REQUIREMENTS_PATH.exists():
        return None

    with open(REQUIREMENTS_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def inspect_project(project_name):
    requirements = load_requirements()

    if requirements is None:
        return (
            "🦫 MASON ERROR\n\n"
            "I could not find the Project Requirements database.\n\n"
            "Expected file:\n"
            "data/project_requirements.json"
        )

    projects = requirements.get("projects", [])

    target_project = None

    for project in projects:
        existing_name = project.get("name", "").lower()

        if project_name.lower() in existing_name:
            target_project = project
            break

    if target_project is None:
        return (
            "🦫 MASON ERROR\n\n"
            f"Project not found:\n{project_name}"
        )

    report = "🦫 PROJECT INSPECTION REPORT\n\n"

    report += f"PROJECT: {target_project.get('name')}\n"
    report += f"PURPOSE: {target_project.get('purpose')}\n\n"

    report += "REQUIRED FILES:\n"

    found_count = 0
    total_files = 0

    for file_path in target_project.get("required_files", []):
        total_files += 1

        if Path(file_path).exists():
            report += f"✅ {file_path}\n"
            found_count += 1
        else:
            report += f"⚠️ {file_path}\n"

    report += "\nREQUIRED COMMANDS:\n"

    for command in target_project.get("required_commands", []):
        report += f"- {command}\n"

    completion = 0

    if total_files > 0:
        completion = round((found_count / total_files) * 100)

    report += "\nCOMPLETION:\n"
    report += f"{completion}%\n\n"

    report += "NEXT STEP:\n"
    report += target_project.get("next_step", "Unknown")

    return report


if __name__ == "__main__":
    print(inspect_project("Hunter"))