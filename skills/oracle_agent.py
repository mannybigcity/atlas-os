from datetime import datetime


def oracle_agent(task):
    task_text = str(task or "").strip()
    task_lower = task_text.lower()

    approval_keywords = [
        "publish",
        "post",
        "send",
        "email",
        "message",
        "dm",
        "contact",
        "customer",
        "client",
        "public",
        "social media",
        "facebook",
        "instagram",
        "tiktok",
        "youtube",
        "ad",
        "advertising",
        "spend",
        "buy",
        "purchase",
        "payment",
        "budget",
        "financial",
        "legal",
        "contract",
        "refund",
        "reputation",
        "press",
        "announcement",
    ]

    blocked_keywords = [
        "delete",
        "remove files",
        "erase",
        "destroy",
        "wipe",
    ]

    approval_required = any(keyword in task_lower for keyword in approval_keywords)
    blocked_action = any(keyword in task_lower for keyword in blocked_keywords)

    if not task_text:
        status = "needs_task"
        summary = "Oracle received no task to analyze."
        recommendation = (
            "Provide a trend, opportunity, threat, market question, AI tool, "
            "or strategic topic for Oracle to evaluate."
        )
        approval_required = False
    elif blocked_action:
        status = "blocked"
        summary = (
            "Oracle identified a requested action that may involve deleting, "
            "erasing, or removing files. This worker does not delete files."
        )
        recommendation = (
            "Do not proceed with deletion. Ask Manny for explicit direction and "
            "use a separate approved process if file cleanup is truly required."
        )
        approval_required = True
    else:
        status = "completed"
        summary = (
            "Oracle reviewed the task as a Kingdom Intelligence and Trend "
            "Watchtower request for RAMFAM KINGDOM, SIS Custom Creations, "
            "FRESH Apparel, and ATLAS."
        )

        if any(word in task_lower for word in ["trend", "trends", "market", "shift"]):
            recommendation = (
                "Track the trend for relevance, urgency, revenue potential, and "
                "risk. Prioritize findings that can help SIS sell more custom "
                "products, help FRESH grow mission-aligned awareness, or help "
                "ATLAS improve Kingdom operations."
            )
        elif any(word in task_lower for word in ["ai", "tool", "software", "automation"]):
            recommendation = (
                "Evaluate the tool by usefulness, cost, setup difficulty, data "
                "risk, and direct value to revenue, customer commitments, or "
                "system improvements before recommending adoption."
            )
        elif any(word in task_lower for word in ["opportunity", "lead", "revenue", "sales"]):
            recommendation = (
                "Rank the opportunity by speed to revenue, customer fit, required "
                "effort, and whether it strengthens existing Kingdom priorities "
                "before expansion."
            )
        elif any(word in task_lower for word in ["threat", "risk", "competitor", "problem"]):
            recommendation = (
                "Document the threat, estimate impact, identify early warning "
                "signals, and recommend a defensive action that protects revenue, "
                "customer trust, and Manny's focus."
            )
        elif approval_required:
            recommendation = (
                "Prepare a clear recommendation and wait for Manny approval before "
                "taking any public, financial, customer-facing, legal, or "
                "reputation-impacting action."
            )
        else:
            recommendation = (
                "Summarize the intelligence, identify the practical business "
                "impact, and recommend the next safest action. Keep actions "
                "internal unless Manny approves a public, financial, "
                "customer-facing, legal, or reputation-impacting step."
            )

    return {
        "agent": "Oracle",
        "status": status,
        "task": task_text,
        "summary": summary,
        "recommendation": recommendation,
        "approval_required": approval_required,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }

if __name__ == "__main__":
    print(oracle_agent("Evaluate a 50 hat order at $19 each with $12 hat cost and $0.75 patch cost."))
