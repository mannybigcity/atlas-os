# skills/office_status.py

from skills.agent_registry import show_agents
from skills.priority_report import alfred_priority_report
from skills.available_agents import show_available_agents


def office_status():
    report = "🦇 OFFICE STATUS REPORT\n\n"

    report += "=== PRIORITIES ===\n\n"
    report += alfred_priority_report()

    report += "\n\n=== AGENT CITY ===\n\n"
    report += show_agents()

    report += "\n\n=== AVAILABLE AGENTS ===\n\n"
    report += show_available_agents()

    return report


if __name__ == "__main__":
    print(office_status())