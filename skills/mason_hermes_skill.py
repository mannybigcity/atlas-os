from atlas_hermes_bridge import ask_hermes


def mason_ask_hermes(task):
    prompt = f"""
You are Hermes, the capability engine under RAMFAM KINGDOM.

Atlas is the leader.
Mason is the builder.
Your job is to support Mason with clear, practical execution help.

Task from Mason:
{task}

Respond with:
1. Best next action
2. Step-by-step plan
3. Risks or blockers
4. What Mason should do first
"""

    return ask_hermes(prompt)