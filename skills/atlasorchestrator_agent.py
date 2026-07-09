from datetime import datetime, timezone
import re


def atlasorchestrator_agent(task):
    """
    Atlas Orchestrator worker.

    Accepts:
        task (str): Mission/task text from Atlas.

    Returns:
        dict: Safe executive orchestration recommendation.
    """
    task_text = str(task or "").strip()
    task_lower = task_text.lower()

    revenue_terms = [
        "price", "pricing", "profit", "revenue", "quote", "order", "invoice",
        "sale", "sales", "purchase", "customer purchase", "business opportunity",
        "estimate", "cost", "margin", "paid", "payment", "deposit"
    ]
    customer_tracking_terms = [
        "customer", "client", "order", "crm", "tracking", "record", "lead",
        "contact", "status", "pipeline"
    ]
    outreach_terms = [
        "follow-up", "follow up", "message", "draft", "outreach", "email",
        "text", "call", "quote communication", "send", "reply", "respond"
    ]
    research_terms = [
        "research", "market scan", "competitor", "tool discovery", "unknown",
        "external information", "compare", "vendor", "supplier", "source"
    ]
    customer_issue_terms = [
        "complaint", "issue", "problem", "refund", "late", "missing",
        "damaged", "wrong", "support", "service"
    ]
    website_terms = [
        "website", "web page", "landing page", "site", "html", "css",
        "domain", "hosting"
    ]
    social_terms = [
        "social", "facebook", "instagram", "tiktok", "post", "reel",
        "content calendar", "caption"
    ]
    financial_terms = [
        "financial", "finance", "budget", "expense", "cash flow", "forecast",
        "bookkeeping", "tax", "profit and loss", "p&l"
    ]
    public_reputation_terms = [
        "public", "publish", "post", "announce", "brand", "reputation",
        "review", "testimonial", "press", "customer-facing", "customer facing"
    ]

    def contains_any(terms):
        return any(term in task_lower for term in terms)

    def add_agent(agent_name, reason):
        if agent_name not in assigned_agents:
            assigned_agents.append(agent_name)
            reports.append({
                "agent": agent_name,
                "status": "assigned",
                "summary": reason
            })

    assigned_agents = []
    reports = []

    is_revenue = contains_any(revenue_terms)
    is_customer_tracking = contains_any(customer_tracking_terms)
    is_outreach = contains_any(outreach_terms)
    is_research = contains_any(research_terms)
    is_customer_issue = contains_any(customer_issue_terms)
    is_website = contains_any(website_terms)
    is_social = contains_any(social_terms)
    is_financial = contains_any(financial_terms)
    is_public_or_reputation = contains_any(public_reputation_terms)

    has_actual_customer_order = (
        ("order" in task_lower or "customer" in task_lower or "client" in task_lower)
        and is_revenue
    )

    if is_revenue or has_actual_customer_order:
        add_agent("Hunter", "Evaluate revenue, pricing, profitability, and opportunity risk first.")
        add_agent("David", "Record or update customer/order details in CRM after Hunter review.")
        add_agent("Amanda", "Draft customer follow-up or quote communication after David records the order.")
        add_agent("Atlas", "Combine worker findings into final executive recommendation.")
    elif is_customer_issue:
        add_agent("Ranger", "Review customer success issue and recommend service-safe next steps.")
        add_agent("David", "Check or update customer/order tracking in CRM.")
        add_agent("Atlas", "Combine worker findings into final executive recommendation.")
    elif is_website:
        add_agent("Taylor", "Review website/project requirements and implementation path.")
        add_agent("Atlas", "Combine worker findings into final executive recommendation.")
    elif is_social:
        add_agent("Micah", "Review social media content, timing, and brand fit.")
        add_agent("Atlas", "Combine worker findings into final executive recommendation.")
    elif is_research:
        add_agent("Scout", "Research unknown external information, tools, competitors, or market context.")
        add_agent("Atlas", "Combine worker findings into final executive recommendation.")
    elif is_financial:
        add_agent("Gideon", "Review financial impact, cash flow, budget, or stability concerns.")
        add_agent("Atlas", "Combine worker findings into final executive recommendation.")
    elif is_customer_tracking:
        add_agent("David", "Review customer/order tracking and CRM needs.")
        add_agent("Atlas", "Combine worker findings into final executive recommendation.")
    elif is_outreach:
        add_agent("David", "Check customer/order context before any follow-up draft.")
        add_agent("Amanda", "Draft customer-safe outreach or follow-up language.")
        add_agent("Atlas", "Combine worker findings into final executive recommendation.")
    else:
        add_agent("Atlas", "Classify mission, identify missing context, and prepare executive recommendation.")

    approval_required = bool(
        is_revenue
        or is_customer_tracking
        or is_outreach
        or is_financial
        or is_public_or_reputation
        or has_actual_customer_order
        or re.search(r"\b(send|publish|approve|buy|purchase|pay|charge|invoice|quote|post)\b", task_lower)
    )

    if not task_text:
        status = "needs_task"
        summary = "No mission text was provided."
        recommendation = "Request a clear mission from Atlas before assigning workers."
        approval_required = True
    else:
        status = "orchestrated"
        summary = "Mission reviewed against Agent Registry delegation rules. Required agents assigned in safe sequence."
        if approval_required:
            recommendation = (
                "Collect all assigned worker reports, then present Atlas with a single executive recommendation. "
                "Do not contact customers, create invoices, approve actions, publish content, or make financial commitments "
                "without Manny approval."
            )
        else:
            recommendation = (
                "Collect all assigned worker reports, combine findings, and return a single executive recommendation to Atlas."
            )

    return {
        "agent": "Atlasorchestrator",
        "status": status,
        "task": task_text,
        "summary": summary,
        "assigned_agents": assigned_agents,
        "reports": reports,
        "recommendation": recommendation,
        "approval_required": approval_required,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

if __name__ == "__main__":
    print(atlasorchestrator_agent("Evaluate a 50 hat order at $19 each with $12 hat cost and $0.75 patch cost."))
