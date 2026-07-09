import json
from pathlib import Path


BLUEPRINTS_PATH = Path("data") / "project_blueprints.json"


def load_blueprints():
    if not BLUEPRINTS_PATH.exists():
        return None

    with open(BLUEPRINTS_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def get_project_blueprint(project_name):
    data = load_blueprints()

    if data is None:
        return (
            "🦫 MASON ERROR\n\n"
            "Project blueprint database not found.\n\n"
            "Expected:\n"
            "data/project_blueprints.json"
        )

    project_name = project_name.lower()

    for blueprint in data.get("blueprints", []):

        name = blueprint.get("name", "").lower()
        owner = blueprint.get("owner", "").lower()

        if project_name in name or project_name == owner:

            report = "🦫 MASON PROJECT BLUEPRINT\n\n"

            report += f"PROJECT: {blueprint.get('name')}\n"
            report += f"OWNER: {blueprint.get('owner')}\n"
            report += f"PRIORITY: {blueprint.get('priority')}\n"
            report += f"STATUS: {blueprint.get('status')}\n\n"

            report += f"PURPOSE:\n{blueprint.get('purpose')}\n\n"

            report += "FILES REQUIRED:\n"
            for file_name in blueprint.get("files", []):
                report += f"- {file_name}\n"

            report += "\nCOMMANDS:\n"
            for command in blueprint.get("commands", []):
                report += f"- {command}\n"

            report += (
                "\nMASON RECOMMENDATION:\n"
                "Review blueprint and begin construction."
            )

            return report

    return (
        "🦫 MASON ERROR\n\n"
        f"No blueprint found for: {project_name}"
    )