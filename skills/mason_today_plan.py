from datetime import datetime


def mason_today_plan(task: str = ""):
    today = datetime.now().strftime("%B %d, %Y")

    if task:
        return f"""🦫 Mason: Ready.

Task:
{task}

Next step:
I need file access/inspection enabled before I can create reports from screenshots.
"""

    return f"""🦫 Mason: Ready.
Date: {today}

Focus:
One visible win.

Priority:
Revenue-first tasks and working systems.

Next step:
Give me a specific build, inspect, or fix task.
"""


if __name__ == "__main__":
    print(mason_today_plan())