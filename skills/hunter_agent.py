from datetime import datetime


def hunter_agent(task, context=None):
    """
    Hunter evaluates revenue opportunities, startup costs, ROI, risks,
    and next actions for RAMFAM KINGDOM.

    Args:
        task (str): Task or opportunity description.

    Returns:
        dict: Hunter's evaluation response.
    """
    if not isinstance(task, str):
        return {
            "agent": "Hunter",
            "status": "error",
            "task": task,
            "summary": "Invalid task input. Hunter requires a task string.",
            "recommendation": "Submit the task again as plain text.",
            "approval_required": True,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }

    clean_task = task.strip()

    if not clean_task:
        return {
            "agent": "Hunter",
            "status": "error",
            "task": clean_task,
            "summary": "No task was provided for evaluation.",
            "recommendation": "Provide a business idea, opportunity, cost question, or revenue action for Hunter to evaluate.",
            "approval_required": False,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }

    lower_task = clean_task.lower()

    approval_keywords = [
        "public",
        "publish",
        "post",
        "advertise",
        "ad campaign",
        "marketing campaign",
        "customer",
        "client",
        "lead",
        "prospect",
        "quote",
        "invoice",
        "payment",
        "purchase",
        "buy",
        "sell",
        "refund",
        "discount",
        "contract",
        "agreement",
        "proposal",
        "email customer",
        "message customer",
        "call customer",
        "reputation",
        "brand",
        "social media",
        "facebook",
        "instagram",
        "tiktok",
        "website",
        "financial",
        "finance",
        "money",
        "revenue",
        "cost",
        "expense",
        "investment",
        "startup cost",
    ]

    approval_required = any(keyword in lower_task for keyword in approval_keywords)

    revenue_keywords = [
        "revenue",
        "profit",
        "sale",
        "sell",
        "lead",
        "customer",
        "client",
        "opportunity",
        "side hustle",
        "business",
        "service",
        "product",
        "quote",
        "order",
        "roi",
        "return",
    ]

    cost_keywords = [
        "cost",
        "expense",
        "startup",
        "equipment",
        "supplies",
        "inventory",
        "software",
        "subscription",
        "labor",
        "budget",
        "investment",
    ]

    urgent_keywords = [
        "today",
        "asap",
        "urgent",
        "now",
        "deadline",
        "immediately",
        "this week",
    ]

    has_revenue_focus = any(keyword in lower_task for keyword in revenue_keywords)
    has_cost_focus = any(keyword in lower_task for keyword in cost_keywords)
    is_urgent = any(keyword in lower_task for keyword in urgent_keywords)

    summary_parts = ["Hunter reviewed the task for revenue potential, cost exposure, risk, and approval needs."]

    if has_revenue_focus:
        summary_parts.append("The task appears connected to revenue generation or customer opportunity.")
    else:
        summary_parts.append("The revenue impact is not yet clear and should be clarified before major effort is spent.")

    if has_cost_focus:
        summary_parts.append("The task may involve costs or investment that should be estimated before action.")
    else:
        summary_parts.append("No clear cost details were provided, so startup or operating cost should be identified.")

    if is_urgent:
        summary_parts.append("The task appears time-sensitive and should be prioritized if it supports revenue or customer commitments.")

    if approval_required:
        recommendation = (
            "Gather the missing details first: target customer, expected revenue, estimated cost, deadline, risk, and Manny's approval status. "
            "Do not take public, financial, customer-facing, or reputation-impacting action until Manny approves."
        )
    elif has_revenue_focus:
        recommendation = (
            "Estimate cost, expected revenue, time required, and risk level. If the opportunity has strong profit potential and low downside, "
            "prepare a simple next-action plan for Manny to review."
        )
    else:
        recommendation = (
            "Clarify the money-making or time-saving purpose before proceeding. If no clear ROI exists, defer this behind revenue generation, "
            "customer commitments, and financial stability."
        )

    return {
        "agent": "Hunter",
        "status": "ready",
        "task": clean_task,
        "summary": " ".join(summary_parts),
        "recommendation": recommendation,
        "approval_required": approval_required,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }

if __name__ == "__main__":
    print(hunter_agent("Evaluate a 50 hat order at $19 each with $12 hat cost and $0.75 patch cost."))
