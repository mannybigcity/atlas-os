# skills/run_the_office.py — Alfred assigns work across Agent City

from revenue.revenue_skill import load_revenue, categorize_revenue_status
from crm.crm_skill import load_prospects
from skills.agent_registry import load_agents
from skills.assign_agent_task import assign_agent_task
from skills.available_agents import show_available_agents


def is_agent_available(agent):
    return agent.get("status", "").lower() in ["standby", "idle"]


def find_available_agent_by_role(role_keyword):
    agents = load_agents()

    for agent in agents:
        role = agent.get("role", "").lower()
        if is_agent_available(agent) and role_keyword.lower() in role:
            return agent.get("name")

    return None


def has_working_agent_by_role(role_keyword):
    agents = load_agents()

    for agent in agents:
        role = agent.get("role", "").lower()
        status = agent.get("status", "").lower()
        if role_keyword.lower() in role and status == "working":
            return True

    return False


def get_top_outstanding_revenue():
    revenue_items = load_revenue()

    outstanding_items = []

    for item in revenue_items:
        status = item.get("status", "")
        category = categorize_revenue_status(status)

        if category == "outstanding":
            outstanding_items.append(item)

    if not outstanding_items:
        return None

    return max(outstanding_items, key=lambda item: float(item.get("amount", 0)))


def get_next_followup():
    prospects = load_prospects()

    followups = [
        prospect for prospect in prospects
        if prospect.get("follow_up")
    ]

    if not followups:
        return None

    followups.sort(key=lambda prospect: prospect.get("follow_up", "9999-99-99"))
    return followups[0]


def run_the_office():
    report = "🦇 ALFRED OFFICE RUN REPORT\n\n"
    assignments = []

    # 1. Finance priority — collect outstanding money
    top_revenue = get_top_outstanding_revenue()

    if top_revenue:
        if has_working_agent_by_role("finance"):
            assignments.append("Finance: Gideon or another Finance Manager is already working.")
        else:
            finance_agent = find_available_agent_by_role("finance")

            if finance_agent:
                customer = top_revenue.get("customer", "the customer")
                source = top_revenue.get("source", "the outstanding payment")
                amount = float(top_revenue.get("amount", 0))
                task = f"Follow up with {customer} about {source} payment for ${amount:.2f}"
                assignments.append(assign_agent_task(finance_agent, task))
            else:
                assignments.append("Finance: Outstanding revenue exists, but no Finance Manager is available.")
    else:
        assignments.append("Finance: No outstanding revenue found.")

    # 2. CRM priority — follow-ups
    next_followup = get_next_followup()

    if next_followup:
        if has_working_agent_by_role("crm"):
            assignments.append("CRM: David or another CRM Manager is already working.")
        else:
            crm_agent = find_available_agent_by_role("crm")

            if crm_agent:
                name = next_followup.get("name", "the prospect")
                business = next_followup.get("business", "their business")
                product = next_followup.get("product", "their project")
                date = next_followup.get("follow_up", "the scheduled date")
                task = f"Review and prepare follow-up for {name} at {business} about {product}, scheduled for {date}"
                assignments.append(assign_agent_task(crm_agent, task))
            else:
                assignments.append("CRM: Follow-ups exist, but no CRM Manager is available.")
    else:
        assignments.append("CRM: No follow-ups scheduled.")

    # 3. Marketing priority — FRESH/SIS content
    if has_working_agent_by_role("social"):
        assignments.append("Marketing: Micah or another Social Media Manager is already working.")
    else:
        social_agent = find_available_agent_by_role("social")

        if social_agent:
            task = "Create today's FRESH or SIS social media sales post focused on generating orders"
            assignments.append(assign_agent_task(social_agent, task))
        else:
            assignments.append("Marketing: No Social Media Manager available.")

    # 4. Marketplace priority — Etsy
    if has_working_agent_by_role("etsy"):
        assignments.append("Marketplace: Amanda or another Etsy Manager is already working.")
    else:
        etsy_agent = find_available_agent_by_role("etsy")

        if etsy_agent:
            task = "Research Etsy listing opportunities for FRESH, SIS, hats, shirts, or custom gifts"
            assignments.append(assign_agent_task(etsy_agent, task))
        else:
            assignments.append("Marketplace: No Etsy Manager available.")

    for item in assignments:
        report += item
        report += "\n\n---\n\n"

    report += show_available_agents()

    return report


if __name__ == "__main__":
    print(run_the_office())