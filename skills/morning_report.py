# skills/morning_report.py — Alfred's upgraded morning report

from skills.executive_briefing import executive_briefing


def alfred_morning_report():
    return executive_briefing()


if __name__ == "__main__":
    print(alfred_morning_report())