# skills/executive_briefing.py

from skills.gideon_report import generate_gideon_report
from skills.david_report import generate_david_report
from skills.micah_report import micah_report
from skills.amanda_report import amanda_report


def executive_briefing():

    report = "🦇 ATLAS EXECUTIVE BRIEFING\n\n"

    report += "=== FINANCE ===\n\n"
    report += generate_gideon_report()

    report += "\n\n====================================\n\n"

    report += "=== CRM ===\n\n"
    report += generate_david_report()

    report += "\n\n====================================\n\n"

    report += "=== MARKETING ===\n\n"
    report += micah_report()

    report += "\n\n====================================\n\n"

    report += "=== MARKETPLACE ===\n\n"
    report += amanda_report()

    return report


if __name__ == "__main__":
    print(executive_briefing())
