import json
from pathlib import Path


PROJECT_STATUS_PATH = Path("data") / "project_statuses.json"


def load_project_statuses():
    if not PROJECT_STATUS_PATH.exists():
        return None

    with open(PROJECT_STATUS_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def save_project_statuses(data):
    with open(PROJECT_STATUS_PATH, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def get_projects_by_status(status_name):
    data = load_project_statuses()

    if data is None:
        return None

    projects = data.get("projects", [])

    return [
        project for project in projects
        if project.get("status", "").lower() == status_name.lower()
    ]


def project_status_report(status_name, report_title):
    data = load_project_statuses()

    if data is None:
        return project_status_missing_error()

    projects = get_projects_by_status(status_name)

    report = f"🦫 {report_title}\n\n"
    report += f"SYSTEM: {data.get('status_system', 'Unknown')}\n"
    report += f"OWNER: {data.get('owner', 'Unknown')}\n\n"
    report += f"{status_name.upper()} PROJECTS:\n"

    if not projects:
        report += "- None\n"
    else:
        for project in projects:
            report += (
                f"- {project.get('name', 'Unknown Project')} | "
                f"Owner: {project.get('owner', 'Unknown')} | "
                f"Priority: {project.get('priority', 'Unknown')}\n"
            )

    return report


def active_projects_report():
    return project_status_report(
        "Building",
        "MASON ACTIVE PROJECTS"
    )


def planned_projects_report():
    return project_status_report(
        "Planned",
        "MASON PLANNED PROJECTS"
    )


def completed_projects_report():
    return project_status_report(
        "Complete",
        "MASON COMPLETED PROJECTS"
    )


def update_project_status(project_name, new_status):
    data = load_project_statuses()

    if data is None:
        return project_status_missing_error()

    allowed_statuses = data.get("allowed_statuses", [])

    if new_status not in allowed_statuses:
        return (
            "🦫 MASON ERROR\n\n"
            f"'{new_status}' is not an allowed status.\n\n"
            f"Allowed statuses: {', '.join(allowed_statuses)}"
        )

    projects = data.get("projects", [])
    search_name = project_name.lower().strip()

    for project in projects:
        existing_name = project.get("name", "").lower()

        if search_name in existing_name or existing_name in search_name:
            old_status = project.get("status", "Unknown")
            project["status"] = new_status

            save_project_statuses(data)

            report = "🦫 PROJECT UPDATED\n\n"
            report += f"Project: {project.get('name', 'Unknown Project')}\n"
            report += f"Old Status: {old_status}\n"
            report += f"New Status: {new_status}\n\n"
            report += "Mason Status:\n"
            report += "Project board updated successfully."

            return report

    return (
        "🦫 MASON ERROR\n\n"
        "I could not find a project matching:\n"
        f"{project_name}"
    )


def create_project(project_name, owner="Mason", priority="Medium"):
    data = load_project_statuses()

    if data is None:
        return project_status_missing_error()

    clean_name = project_name.strip()

    if not clean_name:
        return (
            "🦫 MASON ERROR\n\n"
            "No project name was provided."
        )

    projects = data.get("projects", [])

    for project in projects:
        existing_name = project.get("name", "").lower()

        if clean_name.lower() == existing_name:
            return (
                "🦫 MASON NOTICE\n\n"
                f"Project already exists:\n"
                f"{project.get('name')}\n\n"
                f"Current Status: {project.get('status')}"
            )

    new_project = {
        "name": clean_name,
        "status": "Planned",
        "owner": owner,
        "priority": priority
    }

    projects.append(new_project)
    data["projects"] = projects

    save_project_statuses(data)

    report = "🦫 PROJECT CREATED\n\n"
    report += f"Project: {clean_name}\n"
    report += "Status: Planned\n"
    report += f"Owner: {owner}\n"
    report += f"Priority: {priority}\n\n"
    report += "Mason Status:\n"
    report += "Project added to the Kingdom project board."

    return report


def start_project(project_name):
    return update_project_status(project_name, "Building")


def test_project(project_name):
    return update_project_status(project_name, "Testing")


def complete_project(project_name):
    return update_project_status(project_name, "Complete")


def project_status_missing_error():
    return (
        "🦫 MASON ERROR\n\n"
        "I could not find the Project Status database.\n\n"
        "Expected file:\n"
        "data/project_statuses.json"
    )


if __name__ == "__main__":
    print(active_projects_report())