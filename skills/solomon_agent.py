from datetime import datetime


def solomon_agent(task):
    """
    Solomon the Wise Lion: Kingdom Wisdom Advisor.

    Accepts a task as a string and returns wise counsel for RAMFAM Kingdom decisions.
    This worker does not send messages, publish content, spend money, contact customers,
    delete files, or call external APIs.
    """
    task_text = str(task or "").strip()
    task_lower = task_text.lower()

    approval_triggers = [
        "public",
        "publish",
        "post",
        "announce",
        "social media",
        "website",
        "customer",
        "client",
        "email",
        "message",
        "call",
        "contact",
        "financial",
        "finance",
        "money",
        "spend",
        "buy",
        "purchase",
        "payment",
        "invoice",
        "refund",
        "discount",
        "quote",
        "legal",
        "contract",
        "agreement",
        "partnership",
        "partner",
        "reputation",
        "brand",
        "review",
        "commitment",
        "proposal",
    ]

    risk_triggers = {
        "speed": ["rush", "urgent", "quick", "fast", "immediately", "asap"],
        "money": ["spend", "buy", "purchase", "invest", "payment", "cost", "expense", "financial"],
        "customers": ["customer", "client", "order", "delivery", "promise", "deadline"],
        "public": ["publish", "post", "announce", "public", "launch", "website", "social"],
        "partnership": ["partner", "partnership", "vendor", "agreement", "contract"],
        "capacity": ["scale", "expand", "growth", "new opportunity", "hire", "take on"],
        "files": ["delete", "remove", "overwrite", "erase"],
    }

    approval_required = any(trigger in task_lower for trigger in approval_triggers)

    identified_risks = []
    for category, triggers in risk_triggers.items():
        if any(trigger in task_lower for trigger in triggers):
            identified_risks.append(category)

    if not identified_risks:
        identified_risks.append("unclear scope")

    if "delete" in task_lower or "remove file" in task_lower or "erase" in task_lower:
        recommendation = (
            "Do not delete files. Pause, preserve the current state, create a backup plan, "
            "and ask Manny for approval if the action could affect operations, customers, "
            "finances, reputation, or Kingdom records."
        )
        status = "blocked"
    elif approval_required:
        recommendation = (
            "Pause before action. Prepare a clear decision brief for Manny with the purpose, "
            "cost, risks, customer impact, long-term consequences, and safest next step. "
            "Do not proceed until approval is given."
        )
        status = "approval_required"
    elif not task_text:
        recommendation = (
            "Clarify the decision before moving. A wise answer requires knowing the goal, "
            "stakes, timing, affected people, cost, and risk."
        )
        status = "needs_clarity"
    else:
        recommendation = (
            "Move slowly and wisely. Evaluate whether this protects existing commitments, "
            "strengthens the foundation, avoids unnecessary risk, and aligns with Kingdom "
            "values before taking the next step."
        )
        status = "reviewed"

    summary = (
        "Solomon advises wisdom before speed, stewardship before growth, and foundation "
        "before expansion. The task should be judged by its long-term fruit, hidden risks, "
        "effect on existing commitments, and alignment with Kingdom values. Risks identified: "
        + ", ".join(identified_risks)
        + ". Long-term consequences should be considered before action, especially whether "
        "this creates stability or adds avoidable burden."
    )

    return {
        "agent": "Solomon",
        "status": status,
        "task": task_text,
        "summary": summary,
        "recommendation": recommendation,
        "approval_required": approval_required,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }

if __name__ == "__main__":
    print(solomon_agent("Evaluate a 50 hat order at $19 each with $12 hat cost and $0.75 patch cost."))
