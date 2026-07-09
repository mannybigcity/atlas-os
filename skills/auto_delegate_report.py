# skills/auto_delegate_report.py

from skills.auto_delegate import auto_delegate_next_task
from skills.available_agents import show_available_agents


def alfred_auto_delegate_report():

    report = "🦇 ALFRED AUTO-DELEGATION REPORT\n\n"

    report += auto_delegate_next_task()

    report += "\n\n"
    report += show_available_agents()

    return report


if __name__ == "__main__":
    print(alfred_auto_delegate_report())