# skills/agent_reports.py

from skills.micah_report import micah_report
from skills.gideon_report import generate_gideon_report
from skills.david_report import generate_david_report
from skills.amanda_report import amanda_report


def get_agent_report(agent_name):
    name = agent_name.lower().strip()

    if name == "micah":
        return micah_report()

    if name == "gideon":
        return generate_gideon_report()

    if name == "david":
        return generate_david_report()

    if name == "amanda":
        return amanda_report()

    return f"🦇 Alfred could not find a report for agent: {agent_name}"


if __name__ == "__main__":
    print(get_agent_report("Micah"))