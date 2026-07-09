from datetime import datetime


def mason_agent(task, context=None):
    """
    RAMFAM KINGDOM Mason worker.

    Mason is the Foundry Architect:
    builds, tests, repairs, and reports on Kingdom workers.
    This worker does not send messages, publish posts, spend money,
    contact customers, delete files, or use external APIs.
    """

    task_text = "" if task is None else str(task).strip()
    task_lower = task_text.lower()

    approval_keywords = [
        "public",
        "publish",
        "post",
        "social media",
        "customer",
        "client",
        "email",
        "call",
        "text",
        "sms",
        "dm",
        "message",
        "invoice",
        "quote",
        "estimate",
        "payment",
        "charge",
        "refund",
        "purchase",
        "buy",
        "spend",
        "financial",
        "legal",
        "contract",
        "terms",
        "policy",
        "brand",
        "reputation",
        "review",
        "complaint",
        "announcement",
        "website live",
        "launch",
    ]

    unsafe_keywords = [
        "delete",
        "remove file",
        "erase",
        "wipe",
        "destroy",
        "drop database",
        "format",
    ]

    approval_required = any(keyword in task_lower for keyword in approval_keywords)
    unsafe_requested = any(keyword in task_lower for keyword in unsafe_keywords)

    if not task_text:
        status = "needs_task"
        summary = "No task was provided for Mason to evaluate."
        recommendation = "Provide a clear build, repair, test, or system-improvement task for Mason."
        approval_required = False

    elif unsafe_requested:
        status = "blocked"
        summary = "The task appears to request file deletion or destructive behavior, which Mason is not allowed to perform."
        recommendation = (
            "Do not delete files. Recommend creating a backup, reviewing the target manually, "
            "or asking Manny for explicit direction before any destructive action."
        )
        approval_required = True

    elif approval_required:
        status = "approval_required"
        summary = (
            "The task may affect public presence, finances, customers, legal standing, "
            "or RAMFAM KINGDOM reputation."
        )
        recommendation = (
            "Prepare a safe draft, plan, checklist, or internal report only. "
            "Get Manny approval before taking any public, financial, customer-facing, "
            "legal, or reputation-impacting action."
        )

    else:
        status = "ready"
        summary = (
            "The task appears suitable for Mason as an internal Foundry Architect action "
            "focused on building, testing, repairing, or reporting."
        )
        recommendation = (
            "Proceed with a practical internal implementation plan. Prioritize revenue protection, "
            "customer commitments, system stability, and clear reporting to ATLAS."
        )

    return {
        "agent": "Mason",
        "status": status,
        "task": task_text,
        "summary": summary,
        "recommendation": recommendation,
        "approval_required": approval_required,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }

if __name__ == "__main__":
    print(mason_agent("Evaluate a 50 hat order at $19 each with $12 hat cost and $0.75 patch cost."))
