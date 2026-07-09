from datetime import datetime


def amanda_agent(task, context=None):
    """
    Amanda: RAMFAM KINGDOM Outreach and Marketplace Agent.

    Drafts practical outreach, customer reply, quote, follow-up, and marketplace
    recommendations. Does not send messages, publish posts, spend money, contact
    customers, delete files, or take external actions.

    Manny approval is required before any public, financial, customer-facing,
    legal, or reputation-impacting action.
    """
    if not isinstance(task, str):
        task = str(task)

    clean_task = task.strip()

    approval_keywords = [
        "send",
        "post",
        "publish",
        "customer",
        "client",
        "quote",
        "invoice",
        "price",
        "pricing",
        "discount",
        "refund",
        "payment",
        "order",
        "marketplace",
        "facebook",
        "instagram",
        "email",
        "sms",
        "message",
        "reply",
        "follow up",
        "follow-up",
        "legal",
        "contract",
        "public",
        "review",
        "complaint",
        "reputation",
        "brand",
        "ad",
        "advertisement",
        "spend",
        "purchase",
        "contact",
    ]

    lower_task = clean_task.lower()
    approval_required = any(keyword in lower_task for keyword in approval_keywords)

    if not clean_task:
        summary = "Amanda received an empty task."
        recommendation = (
            "Provide a specific outreach, marketplace, quote, follow-up, or customer "
            "communication task for Amanda to draft or review."
        )
        status = "needs_task"
        approval_required = False
    else:
        status = "draft_ready"

        if any(word in lower_task for word in ["quote", "price", "pricing", "invoice", "estimate"]):
            summary = "Amanda identified this as a quote or pricing-related task."
            recommendation = (
                "Prepare a clear draft with item details, quantities, timeline, payment terms, "
                "and any assumptions. Manny must approve before it is shared with the customer."
            )
        elif any(word in lower_task for word in ["follow up", "follow-up", "reply", "message", "email", "sms"]):
            summary = "Amanda identified this as a customer or prospect communication task."
            recommendation = (
                "Draft a polite, concise message that confirms the need, gives the next step, "
                "and protects the RAMFAM KINGDOM brand. Manny must approve before sending."
            )
        elif any(word in lower_task for word in ["marketplace", "facebook", "instagram", "post", "publish", "ad"]):
            summary = "Amanda identified this as a marketplace or public outreach task."
            recommendation = (
                "Create a practical draft with a strong offer, clear call to action, and no unsupported claims. "
                "Manny must approve before anything is posted or published."
            )
        elif any(word in lower_task for word in ["complaint", "refund", "problem", "issue", "review"]):
            summary = "Amanda identified this as a reputation-sensitive customer care task."
            recommendation = (
                "Draft a calm response that acknowledges the concern, avoids blame, offers a next step, "
                "and escalates to Manny for approval before responding."
            )
        else:
            summary = "Amanda reviewed the task for outreach and marketplace support."
            recommendation = (
                "Prepare a practical draft or action plan that supports RAMFAM KINGDOM, SIS Custom Creations, "
                "FRESH Apparel, or ATLAS. Do not send, publish, spend, contact customers, or delete files."
            )

    return {
        "agent": "Amanda",
        "status": status,
        "task": clean_task,
        "summary": summary,
        "recommendation": recommendation,
        "approval_required": approval_required,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }

if __name__ == "__main__":
    print(amanda_agent("Evaluate a 50 hat order at $19 each with $12 hat cost and $0.75 patch cost."))
