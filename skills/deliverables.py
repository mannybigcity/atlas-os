# skills/deliverables.py

from skills.micah_deliverable import generate_micah_deliverables
from skills.amanda_deliverable import generate_amanda_deliverables
from skills.david_deliverable import generate_david_deliverables
from skills.gideon_deliverable import generate_gideon_deliverables


def create_deliverable(agent_name, deliverable_type="", target=""):
    agent = agent_name.lower().strip()

    if agent == "micah":
        return generate_micah_deliverables()

    if agent == "amanda":
        return generate_amanda_deliverables()

    if agent == "david":
        return generate_david_deliverables()

    if agent == "gideon":
        return generate_gideon_deliverables()

    return (
        f"🦇 Alfred could not create that deliverable yet.\n\n"
        f"Agent: {agent_name}"
    )


if __name__ == "__main__":
    print(create_deliverable("Micah"))