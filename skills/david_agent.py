from datetime import datetime


def david_agent(task, context=None):
    task_text = str(task or "").strip()
    task_lower = task_text.lower()

    approval_keywords = [
        "send",
        "message",
        "email",
        "text",
        "call",
        "contact",
        "customer",
        "client",
        "lead",
        "public",
        "post",
        "publish",
        "financial",
        "invoice",
        "payment",
        "refund",
        "charge",
        "spend",
        "buy",
        "purchase",
        "legal",
        "contract",
        "reputation",
        "review",
        "delete",
        "remove file",
    ]

    approval_required = any(keyword in task_lower for keyword in approval_keywords)

    if not task_text:
        summary = "No CRM task was provided for David."
        recommendation = "Provide a clear CRM task involving leads, customers, orders, follow-ups, statuses, or next actions."
        status = "needs_task"
    elif "delete" in task_lower or "remove file" in task_lower:
        summary = "David identified a restricted request involving deletion."
        recommendation = "Do not delete files. Recommend archiving, flagging, or asking Manny for direction before any destructive action."
        status = "blocked"
        approval_required = True
    elif any(word in task_lower for word in ["send", "message", "email", "text", "call", "contact"]):
        summary = "David identified a customer-facing or communication-related CRM task."
        recommendation = "Prepare a draft, customer record update, or follow-up plan only. Manny approval is required before contacting anyone."
        status = "approval_required"
        approval_required = True
    elif any(word in task_lower for word in ["invoice", "payment", "refund", "charge", "spend", "buy", "purchase"]):
        summary = "David identified a financial CRM task."
        recommendation = "Organize the relevant CRM details and prepare a recommendation. Manny approval is required before any financial action."
        status = "approval_required"
        approval_required = True
    elif any(word in task_lower for word in ["post", "publish", "public", "review", "reputation"]):
        summary = "David identified a public or reputation-impacting task."
        recommendation = "Prepare internal notes or a draft only. Manny approval is required before anything public is released."
        status = "approval_required"
        approval_required = True
    elif any(word in task_lower for word in ["lead", "prospect"]):
        summary = "David should organize the lead details, identify current status, and define the next follow-up step."
        recommendation = "Capture lead name, business, need, source, priority, last touch, next action, owner, and follow-up date."
        status = "ready"
    elif any(word in task_lower for word in ["customer", "client"]):
        summary = "David should update or review the customer record and clarify the next action."
        recommendation = "Verify customer status, open orders, promises made, deadlines, follow-up needs, and any risks requiring ATLAS awareness."
        status = "ready"
    elif any(word in task_lower for word in ["order", "job", "quote", "estimate"]):
        summary = "David should organize the order or quote status and identify any missing information."
        recommendation = "Track customer name, product/service, quantity, deadline, price status, production status, payment status, and next action."
        status = "ready"
    elif any(word in task_lower for word in ["follow", "follow-up", "next action", "next step"]):
        summary = "David should prioritize follow-ups and make the next action clear."
        recommendation = "Sort follow-ups by customer commitment, revenue impact, deadline urgency, and relationship risk."
        status = "ready"
    else:
        summary = "David reviewed the CRM task and found no restricted action required by default."
        recommendation = "Convert the request into a clear CRM record update with status, owner, priority, next action, and follow-up date."
        status = "ready"

    return {
        "agent": "David",
        "status": status,
        "task": task_text,
        "summary": summary,
        "recommendation": recommendation,
        "approval_required": approval_required,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }

if __name__ == "__main__":
    print(david_agent("Evaluate a 50 hat order at $19 each with $12 hat cost and $0.75 patch cost."))
