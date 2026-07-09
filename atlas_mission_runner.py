import json
import os
from datetime import datetime

from skills.atlasorchestrator_agent import atlasorchestrator_agent

WORKERS = {
    "Hunter": "skills.hunter_agent",
    "David": "skills.david_agent",
    "Amanda": "skills.amanda_agent",
    "Atlas": "skills.atlas_agent",
}


def load_worker(agent_name):
    module_name = WORKERS.get(agent_name)
    if not module_name:
        return None

    module = __import__(module_name, fromlist=[""])
    function_name = f"{agent_name.lower()}_agent"
    return getattr(module, function_name, None)


def save_report(report):
    mission_folder = r"C:\Users\User\Desktop\PUTER\RAMFAM_KINGDOM_BRAIN\06_MISSIONS"
    os.makedirs(mission_folder, exist_ok=True)

    latest_file = os.path.join(mission_folder, "mission_report_latest.json")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_file = os.path.join(mission_folder, f"mission_{timestamp}.json")

    with open(latest_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    with open(archive_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("\nMission saved:")
    print(latest_file)
    print(archive_file)


def run_mission(task):
    plan = atlasorchestrator_agent(task)
    assigned_agents = plan.get("assigned_agents", [])

    print("\n=== ATLAS MISSION PLAN ===")
    print("Task:", task)
    print("Assigned Agents:", assigned_agents)
    print("Approval Required:", plan.get("approval_required", True))

    worker_outputs = []

    print("\n=== WORKER REPORTS ===")
    for agent in assigned_agents:
        worker = load_worker(agent)

        if not worker:
            print(f"- {agent}: No worker found.")
            worker_outputs.append({
                "agent": agent,
                "status": "missing_worker",
                "summary": "No worker function was found for this agent.",
                "approval_required": True
            })
            continue

        try:
            result = worker(task)
            worker_outputs.append(result)
            print(f"- {agent}: {result.get('summary', result)}")
        except Exception as e:
            error_report = {
                "agent": agent,
                "status": "error",
                "summary": str(e),
                "approval_required": True
            }
            worker_outputs.append(error_report)
            print(f"- {agent}: ERROR - {e}")

    report = {
        "mission": task,
        "plan": plan,
        "worker_outputs": worker_outputs,
        "approval_required": True,
        "created": datetime.now().isoformat()
    }

    save_report(report)

    print("\n=== FINAL EXECUTIVE PACKAGE READY ===")
    print("Mission complete. Manny approval still required.")

    return report


if __name__ == "__main__":
    run_mission(
        "Customer wants 50 hats at $19 each. Cost is $12 hat plus $0.75 patch. Route this mission."
    )
