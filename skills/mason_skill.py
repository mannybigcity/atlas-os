import json
from pathlib import Path

from skills.project_blueprint_skill import get_project_blueprint
from skills.project_status_skill import (
    active_projects_report,
    planned_projects_report,
    completed_projects_report,
    create_project,
    start_project,
    test_project,
    complete_project
)
from skills.project_inspector_skill import inspect_project
from skills.revenue_campaign_skill import launch_revenue_campaign
from skills.mason_recommendation_skill import (
    mason_recommend_next_project,
    mason_recommend_revenue_action,
    mason_find_bottleneck
)


BLUEPRINT_PATH = Path("data") / "kingdom_blueprint.json"
CONSTRUCTION_LOG_PATH = Path("data") / "construction_log.json"
INSPECTION_PATH = Path("data") / "kingdom_inspection.json"

HUNTER_MAPS_TARGETS_PATH = Path("data") / "hunter_maps_targets.json"
HUNTER_PIPELINE_PATH = Path("data") / "hunter_pipeline.json"
HUNTER_LEADS_PATH = Path("data") / "hunter_leads.json"
AMANDA_OUTREACH_PATH = Path("data") / "amanda_outreach.json"
SCOUT_OPPORTUNITIES_PATH = Path("data") / "scout_opportunities.json"


def load_json(path):
    if not path.exists():
        return None

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_blueprint():
    return load_json(BLUEPRINT_PATH)


def load_construction_log():
    return load_json(CONSTRUCTION_LOG_PATH)


def load_inspection():
    return load_json(INSPECTION_PATH)


def check_file_exists(folder_name, file_name):
    return (Path(folder_name) / file_name).exists()


def mason_launch_revenue_campaign():
    return launch_revenue_campaign()


def mason_next_project_recommendation():
    return mason_recommend_next_project()


def mason_revenue_recommendation():
    return mason_recommend_revenue_action()


def mason_bottleneck_report():
    return mason_find_bottleneck()


def mason_project_blueprint(project_name):
    return get_project_blueprint(project_name)


def mason_active_projects():
    return active_projects_report()


def mason_planned_projects():
    return planned_projects_report()


def mason_completed_projects():
    return completed_projects_report()


def mason_create_project(project_name):
    return create_project(project_name)


def mason_start_project(project_name):
    return start_project(project_name)


def mason_test_project(project_name):
    return test_project(project_name)


def mason_complete_project(project_name):
    return complete_project(project_name)


def mason_inspect_project(project_name):
    return inspect_project(project_name)


def mason_build_today_mission():
    maps_data = load_json(HUNTER_MAPS_TARGETS_PATH) or {}
    pipeline_data = load_json(HUNTER_PIPELINE_PATH) or {}
    leads_data = load_json(HUNTER_LEADS_PATH) or {}
    outreach_data = load_json(AMANDA_OUTREACH_PATH) or {}
    scout_data = load_json(SCOUT_OPPORTUNITIES_PATH) or {}

    maps_targets = maps_data.get("targets", [])
    pipeline = pipeline_data.get("pipeline", [])
    leads = leads_data.get("leads", [])
    outreach_queue = outreach_data.get("outreach_queue", [])
    scout_opportunities = scout_data.get("opportunities", [])

    high_score_targets = [
        target for target in maps_targets
        if int(target.get("opportunity_score", 0)) >= 8
    ]

    pending_outreach = [
        item for item in outreach_queue
        if item.get("status") == "Pending Contact"
    ]

    contacted_outreach = [
        item for item in outreach_queue
        if item.get("status") == "Contacted"
    ]

    report = "🦫 MASON DAILY MISSION PLAN\n\n"

    report += "KINGDOM SNAPSHOT:\n"
    report += f"- Hunter Maps Targets: {len(maps_targets)}\n"
    report += f"- High Score Maps Targets: {len(high_score_targets)}\n"
    report += f"- Hunter Leads: {len(leads)}\n"
    report += f"- Hunter Pipeline Records: {len(pipeline)}\n"
    report += f"- Scout Opportunities: {len(scout_opportunities)}\n"
    report += f"- Amanda Pending Outreach: {len(pending_outreach)}\n"
    report += f"- Amanda Contacted Outreach: {len(contacted_outreach)}\n\n"

    report += "TODAY'S MISSIONS:\n\n"

    report += "MISSION 1 — HUNTER\n"
    report += "Run live Google Maps searches and collect website opportunities.\n"
    report += "Search targets:\n"
    report += "- HVAC in Cypress\n"
    report += "- Roofers in Katy\n"
    report += "- Plumbers in Tomball\n"
    report += "- Pressure washing in Houston\n"
    report += "- Auto detailing in Spring\n\n"

    report += "MISSION 2 — SCOUT\n"
    report += "Review Hunter Maps targets and turn strong targets into Scout opportunities.\n\n"

    report += "MISSION 3 — AMANDA\n"

    if pending_outreach:
        report += "Work the pending outreach queue first.\n"
    elif high_score_targets:
        report += "Prepare outreach for the highest-score Hunter Maps targets.\n"
    else:
        report += "Stand by until Hunter produces new targets.\n"

    report += "\nMISSION 4 — DAVID\n"
    report += "Track follow-ups for Kandy, Bobby, and any contacted website leads.\n\n"

    report += "MISSION 5 — GIDEON\n"
    report += "Track money due and estimate value of website opportunities.\n\n"

    report += "KING'S FOCUS:\n"
    report += "Do not build random features. Feed the sales pipeline with real business targets."

    return report


def mason_recommend_next_build_live():
    maps_data = load_json(HUNTER_MAPS_TARGETS_PATH) or {}
    pipeline_data = load_json(HUNTER_PIPELINE_PATH) or {}
    outreach_data = load_json(AMANDA_OUTREACH_PATH) or {}

    maps_targets = maps_data.get("targets", [])
    pipeline = pipeline_data.get("pipeline", [])
    outreach_queue = outreach_data.get("outreach_queue", [])

    pending_outreach = [
        item for item in outreach_queue
        if item.get("status") == "Pending Contact"
    ]

    high_score_targets = [
        target for target in maps_targets
        if int(target.get("opportunity_score", 0)) >= 8
    ]

    report = "🦫 MASON NEXT BUILD RECOMMENDATION\n\n"

    report += "CURRENT SYSTEM STATUS:\n"
    report += f"- Hunter Maps Targets: {len(maps_targets)}\n"
    report += f"- High Score Targets: {len(high_score_targets)}\n"
    report += f"- Hunter Pipeline Records: {len(pipeline)}\n"
    report += f"- Pending Amanda Outreach: {len(pending_outreach)}\n\n"

    if not maps_targets:
        report += "RECOMMENDED BUILD:\n"
        report += "Hunter Maps Auto-Save System\n\n"
        report += "WHY:\n"
        report += "Hunter can search Google Maps, but the results are not automatically saved yet.\n\n"
        report += "REVENUE IMPACT:\n"
        report += "Very High\n\n"
        report += "NEXT STEP:\n"
        report += "Build Hunter, hunt <industry> in <city> command."
        return report

    if maps_targets and not high_score_targets:
        report += "RECOMMENDED BUILD:\n"
        report += "Hunter Maps Scoring Upgrade\n\n"
        report += "WHY:\n"
        report += "Hunter has targets, but needs better scoring for website opportunities.\n\n"
        report += "REVENUE IMPACT:\n"
        report += "High\n\n"
        report += "NEXT STEP:\n"
        report += "Improve weak/no website detection."
        return report

    if high_score_targets and not pending_outreach:
        report += "RECOMMENDED BUILD:\n"
        report += "Hunter Maps → Amanda Handoff\n\n"
        report += "WHY:\n"
        report += "Hunter has high-score targets, but Amanda is not automatically receiving them.\n\n"
        report += "REVENUE IMPACT:\n"
        report += "Very High\n\n"
        report += "NEXT STEP:\n"
        report += "Build command: Hunter, send maps target to Amanda."
        return report

    if pending_outreach:
        report += "RECOMMENDED BUILD:\n"
        report += "Do not build. Execute outreach.\n\n"
        report += "WHY:\n"
        report += "Amanda has pending outreach. The bottleneck is action, not code.\n\n"
        report += "REVENUE IMPACT:\n"
        report += "Immediate\n\n"
        report += "NEXT STEP:\n"
        report += "Contact pending leads."
        return report

    report += "RECOMMENDED BUILD:\n"
    report += "Hunter Maps Automation v2\n\n"
    report += "WHY:\n"
    report += "The system is ready to automate lead hunting by industry and city.\n\n"
    report += "NEXT STEP:\n"
    report += "Build live search importer."

    return report


def mason_report():
    blueprint = load_blueprint()

    if blueprint is None:
        return (
            "🦫 MASON ERROR\n\n"
            "I could not find the Kingdom Blueprint.\n\n"
            "Expected file:\n"
            "data/kingdom_blueprint.json"
        )

    report = "🦫 MASON BLUEPRINT REPORT\n\n"

    report += f"KINGDOM: {blueprint.get('kingdom_name', 'Unknown')}\n"
    report += f"MISSION: {blueprint.get('mission', 'Unknown')}\n"
    report += f"PRINCIPLE: {blueprint.get('principle', 'Unknown')}\n\n"

    report += "ACTIVE AGENTS:\n"
    for agent in blueprint.get("existing_agents", []):
        report += f"- {agent.get('name')} | {agent.get('role')} | {agent.get('status')}\n"

    report += "\nPLANNED AGENTS:\n"
    for agent in blueprint.get("planned_agents", []):
        report += f"- {agent.get('name')} | {agent.get('role')} | {agent.get('status')}\n"

    report += "\nEXISTING SYSTEMS:\n"
    for system in blueprint.get("existing_systems", []):
        report += f"- {system}\n"

    report += "\nPLANNED SYSTEMS:\n"
    for system in blueprint.get("planned_systems", []):
        report += f"- {system}\n"

    priority = blueprint.get("current_priority", {})

    report += "\nCURRENT PRIORITY:\n"
    report += f"Project: {priority.get('project', 'Unknown')}\n"
    report += f"Reason: {priority.get('reason', 'Unknown')}\n"
    report += f"Recommended Next Build: {priority.get('recommended_next_build', 'Unknown')}\n"

    report += "\nCONSTRUCTION LOG:\n"
    for item in blueprint.get("construction_log", []):
        report += (
            f"- {item.get('project')} | "
            f"{item.get('status')} | "
            f"{item.get('notes')}\n"
        )

    return report


def mason_next_build():
    return mason_recommend_next_build_live()


def mason_construction_log():
    construction_log = load_construction_log()

    if construction_log is None:
        return (
            "🦫 MASON ERROR\n\n"
            "I could not find the Construction Log.\n\n"
            "Expected file:\n"
            "data/construction_log.json"
        )

    projects = construction_log.get("projects", [])

    status_order = [
        "Building",
        "Testing",
        "Planned",
        "Complete"
    ]

    report = "🦫 MASON CONSTRUCTION LOG\n\n"

    report += f"LOG: {construction_log.get('log_name', 'Unknown')}\n"
    report += f"MISSION: {construction_log.get('mission', 'Unknown')}\n\n"

    for status in status_order:
        matching_projects = [
            project for project in projects
            if project.get("status", "").lower() == status.lower()
        ]

        report += f"{status.upper()}:\n"

        if not matching_projects:
            report += "- None\n"
        else:
            for project in matching_projects:
                report += (
                    f"- {project.get('project', 'Unknown Project')} | "
                    f"Priority: {project.get('priority', 'Unknown')} | "
                    f"Owner: {project.get('owner', 'Unknown')}\n"
                    f"  Notes: {project.get('notes', 'No notes')}\n"
                )

        report += "\n"

    report += (
        "Mason Status:\n"
        "Construction Log read-only mode is active. "
        "Project status control is handled through the Project Status Manager."
    )

    return report


def mason_inspect_kingdom():
    inspection = load_inspection()

    if inspection is None:
        return (
            "🦫 MASON ERROR\n\n"
            "I could not find the Kingdom Inspection file.\n\n"
            "Expected file:\n"
            "data/kingdom_inspection.json"
        )

    report = "🦫 KINGDOM INSPECTION REPORT\n\n"

    report += f"INSPECTION: {inspection.get('inspection_name', 'Unknown')}\n"
    report += f"PHASE: {inspection.get('phase', 'Unknown')}\n\n"

    report += "DATA FILES:\n"
    missing_data_files = []

    for file_name in inspection.get("required_data_files", []):
        if check_file_exists("data", file_name):
            report += f"✅ {file_name}\n"
        else:
            report += f"⚠️ {file_name}\n"
            missing_data_files.append(file_name)

    report += "\nAGENT SKILLS:\n"
    missing_agent_skills = []

    for file_name in inspection.get("required_agent_skills", []):
        if check_file_exists("skills", file_name):
            report += f"✅ {file_name}\n"
        else:
            report += f"⚠️ {file_name}\n"
            missing_agent_skills.append(file_name)

    report += "\nFUTURE SYSTEMS:\n"
    for system in inspection.get("required_future_systems", []):
        report += f"- {system}\n"

    report += "\nSUMMARY:\n"
    report += f"Missing Data Files: {len(missing_data_files)}\n"
    report += f"Missing Agent Skills: {len(missing_agent_skills)}\n\n"

    if missing_agent_skills:
        report += "MISSING AGENT SKILLS:\n"
        for file_name in missing_agent_skills:
            report += f"- {file_name}\n"
        report += "\n"

    report += "KINGDOM STATUS:\n"

    if missing_data_files:
        report += "Foundation needs repair. Some required data files are missing.\n"
    elif missing_agent_skills:
        report += "Foundation is active. Planned agents still need skill files.\n"
    else:
        report += "Foundation is strong. Required data files and agent skills exist.\n"

    report += "\nMASON RECOMMENDATION:\n"
    report += "Use Mason's live recommendation engine to choose the next revenue-focused action."

    return report


if __name__ == "__main__":
    print(mason_recommend_next_build_live())