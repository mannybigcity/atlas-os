from datetime import datetime


def atlas_agent(task):
    """
    Atlas Chief of Staff worker for RAMFAM KINGDOM.

    Accepts:
        task (str): The request, situation, decision, or action needing review.

    Returns:
        dict: Atlas recommendation package.
    """
    if task is None:
        task = ""

    task_text = str(task).strip()
    task_lower = task_text.lower()

    approval_triggers = [
        "public",
        "publish",
        "post",
        "announce",
        "social media",
        "customer",
        "client",
        "buyer",
        "order",
        "invoice",
        "refund",
        "quote",
        "proposal",
        "contract",
        "legal",
        "financial",
        "finance",
        "money",
        "payment",
        "purchase",
        "spend",
        "expense",
        "budget",
        "price",
        "pricing",
        "discount",
        "reputation",
        "review",
        "complaint",
        "commitment",
        "deadline",
        "delivery",
    ]

    approval_required = any(trigger in task_lower for trigger in approval_triggers)

    revenue_terms = [
        "sale",
        "sales",
        "revenue",
        "lead",
        "quote",
        "invoice",
        "customer",
        "client",
        "order",
        "payment",
        "follow up",
        "follow-up",
        "opportunity",
    ]

    commitment_terms = [
        "deadline",
        "due",
        "delivery",
        "deliver",
        "existing customer",
        "current customer",
        "open order",
        "pending order",
        "commitment",
        "promised",
    ]

    foundation_terms = [
        "system",
        "process",
        "workflow",
        "automation",
        "crm",
        "organize",
        "structure",
        "documentation",
        "foundation",
    ]

    risk_terms = [
        "urgent",
        "late",
        "angry",
        "complaint",
        "refund",
        "legal",
        "public",
        "reputation",
        "mistake",
        "delay",
        "overdue",
        "failed",
    ]

    is_revenue = any(term in task_lower for term in revenue_terms)
    is_commitment = any(term in task_lower for term in commitment_terms)
    is_foundation = any(term in task_lower for term in foundation_terms)
    is_risk = any(term in task_lower for term in risk_terms)

    if not task_text:
        summary = "No task was provided for Atlas to evaluate."
        recommendation = "Provide a clear task, decision, opportunity, or issue so Atlas can prioritize it and assign the right Kingdom agent."
        status = "needs_task"
    elif is_commitment:
        summary = "This appears connected to an existing commitment or deadline."
        recommendation = "Prioritize this before new opportunities. Protect customer trust, complete the commitment, and assign Ranger or the responsible business agent to drive follow-through."
        status = "priority_existing_commitment"
    elif is_revenue:
        summary = "This appears connected to revenue generation or customer opportunity."
        recommendation = "Prioritize this as a revenue activity. Assign Hunter to evaluate the opportunity, David to track it in CRM if needed, and Ranger or Amanda for follow-up depending on whether it is customer success or outreach."
        status = "priority_revenue"
    elif is_risk:
        summary = "This contains potential risk to trust, reputation, timing, or stability."
        recommendation = "Slow down, protect the Kingdom, and review before action. Assign Atlas to coordinate, Solomon for wisdom review if the decision is sensitive, and Manny for approval before any external action."
        status = "priority_risk_review"
    elif is_foundation:
        summary = "This appears to strengthen systems, workflow, or operational foundation."
        recommendation = "Proceed after revenue and current commitments are protected. Assign Mason for system architecture or David for CRM/process structure."
        status = "priority_foundation"
    else:
        summary = "This task needs coordination and prioritization before execution."
        recommendation = "Rank it against revenue, existing commitments, family stability, system improvements, and strategic expansion. Assign the most relevant Kingdom agent before Manny spends focus on execution."
        status = "needs_prioritization"

    return {
        "agent": "Atlas",
        "status": status,
        "task": task_text,
        "summary": summary,
        "recommendation": recommendation,
        "approval_required": approval_required,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }

if __name__ == "__main__":
    print(atlas_agent("Evaluate a 50 hat order at $19 each with $12 hat cost and $0.75 patch cost."))
