# skills/alfred_deliverable.py


def generate_alfred_deliverables():
    chief_of_staff_briefing = """🐶 ALFRED DELIVERABLE

CHIEF OF STAFF BRIEFING

Alfred, give Manny a clear command center briefing.

Report:
- What is working
- What is broken
- What needs money attention
- What needs marketing attention
- What should Manny do next
"""

    focus_reset = """FOCUS RESET

Sir, pause for 30 seconds.

Breathe.

The mission is not to do everything.

The mission is to do the next right thing.

Current priority:
1. Protect the system
2. Move money forward
3. Build one useful feature at a time
"""

    command_center_task = """COMMAND CENTER TASK

Alfred, inspect PUTER and report:

- Active agents
- Open missions
- Revenue status
- Outstanding invoices
- Follow-ups
- Next best action
"""

    motivation = """MOTIVATION

Sir, we are not playing.

We are building the command center for the RAMFAM.

One file at a time.
One agent at a time.
One paid order at a time.

Proceed.
"""

    return "\n\n".join([
        chief_of_staff_briefing,
        focus_reset,
        command_center_task,
        motivation
    ])