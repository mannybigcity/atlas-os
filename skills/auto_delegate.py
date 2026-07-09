# skills/auto_delegate.py — ATLAS automatically assigns best available RAMFAM KINGDOM agent

from revenue.revenue_skill import load_revenue, categorize_revenue_status
from skills.agent_registry import load_agents
from skills.assign_agent_task import assign_agent_task


def find_available_agent_by_role(role_keyword):
    agents = load_agents()

    for agent in agents:
        status = agent.get("status", "").lower()
        role = agent.get("role", "").lower()

        if status in ["active", "working", "standby", "idle"] and role_keyword.lower() in role:
            return agent.get("name")

    return None


def auto_delegate_next_task():
    revenue_items = load_revenue()

    outstanding_items = []

    for item in revenue_items:
        status = item.get("status", "")
        category = categorize_revenue_status(status)

        if category == "outstanding":
            outstanding_items.append(item)

    if outstanding_items:
        top_item = max(
            outstanding_items,
            key=lambda item: float(item.get("amount", 0))
        )

        agent_name = find_available_agent_by_role("finance")

        if not agent_name:
            return "🦁 ATLAS found outstanding revenue, but no Finance Manager is available."

        customer = top_item.get("customer", "the customer")
        source = top_item.get("source", "the outstanding payment")
        amount = float(top_item.get("amount", 0))

        task = f"Follow up with {customer} about {source} payment for ${amount:.2f}"

        return assign_agent_task(agent_name, task)

    agent_name = find_available_agent_by_role("social")

    if agent_name:
        task = "Create a fresh sales or marketing post for FRESH and SIS"
        return assign_agent_task(agent_name, task)

    return "🦁 ATLAS did not find a money task or available marketing agent to assign."


if __name__ == "__main__":
    print(auto_delegate_next_task())