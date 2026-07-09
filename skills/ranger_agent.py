from datetime import datetime


def ranger_agent(task):
    """
    Ranger Customer Success Agent worker for RAMFAM KINGDOM.

    Accepts a task string and returns a safe, practical customer-success recommendation.
    Does not contact customers, send messages, publish, spend money, delete files, or use external APIs.
    """

    task_text = str(task).strip() if task is not None else ""
    task_lower = task_text.lower()

    approval_keywords = [
        "customer",
        "client",
        "public",
        "post",
        "publish",
        "send",
        "email",
        "text",
        "sms",
        "call",
        "reply",
        "respond",
        "refund",
        "discount",
        "credit",
        "charge",
        "invoice",
        "payment",
        "money",
        "financial",
        "legal",
        "review",
        "complaint",
        "reputation",
        "apology",
        "compensation",
        "cancel order",
        "order update",
        "delivery update",
        "service recovery",
    ]

    approval_required = any(keyword in task_lower for keyword in approval_keywords)

    if not task_text:
        status = "needs_task"
        summary = "No customer-success task was provided for Ranger to review."
        recommendation = (
            "Provide a clear task involving customer care, order updates, service recovery, "
            "satisfaction, retention, or support for RAMFAM KINGDOM, SIS Custom Creations, "
            "FRESH Apparel, or ATLAS."
        )
        approval_required = False
    else:
        status = "ready_for_review"

        if any(word in task_lower for word in ["complaint", "unhappy", "angry", "upset", "bad review", "issue", "problem"]):
            summary = "This appears to be a service recovery or customer satisfaction issue."
            recommendation = (
                "Review the situation, gather order details, identify the root issue, and prepare a calm, "
                "ownership-focused response for Manny approval. Recommend a practical recovery option such as "
                "a corrected update, revised timeline, remake review, refund review, or goodwill gesture only "
                "after approval."
            )
            approval_required = True

        elif any(word in task_lower for word in ["order", "status", "update", "tracking", "delivery", "pickup", "ship"]):
            summary = "This appears to involve an order status or fulfillment update."
            recommendation = (
                "Verify the order details internally, confirm the current production or delivery stage, and draft "
                "a clear update with the next expected milestone. Do not send the update to the customer until "
                "Manny approval is given."
            )
            approval_required = True

        elif any(word in task_lower for word in ["refund", "discount", "credit", "payment", "invoice", "charge", "price"]):
            summary = "This appears to involve a financial customer-success decision."
            recommendation = (
                "Collect the order facts, customer concern, requested resolution, and financial impact. Present "
                "Manny with options and a recommended path. Do not offer refunds, discounts, credits, or payment "
                "changes without approval."
            )
            approval_required = True

        elif any(word in task_lower for word in ["retention", "follow up", "satisfaction", "repeat", "loyalty"]):
            summary = "This appears to involve customer retention or satisfaction improvement."
            recommendation = (
                "Prepare a customer-care plan that protects the relationship, confirms satisfaction, and identifies "
                "the next helpful step. If the plan involves contacting a customer or making an offer, Manny approval "
                "is required before action."
            )

        elif any(word in task_lower for word in ["sis", "custom creations", "shirt", "hat", "laser", "engraving", "sign", "apparel"]):
            summary = "This appears related to SIS Custom Creations customer care or order support."
            recommendation = (
                "Organize the request by customer, product type, deadline, order stage, blocker, and recommended "
                "next action. Escalate anything customer-facing, financial, or reputation-impacting for Manny approval."
            )

        elif any(word in task_lower for word in ["fresh", "faithfully", "meal", "apparel"]):
            summary = "This appears related to FRESH Apparel customer success or brand support."
            recommendation = (
                "Frame the response with care, faith-centered professionalism, and brand protection. Prepare the "
                "recommended action internally first, and request Manny approval before any public or customer-facing step."
            )

        elif any(word in task_lower for word in ["atlas", "ramfam", "kingdom"]):
            summary = "This appears related to RAMFAM KINGDOM or ATLAS support coordination."
            recommendation = (
                "Summarize the customer-success need, clarify ownership, identify the safest next step, and route "
                "any customer-facing or reputation-impacting decision to Manny for approval."
            )

        else:
            summary = "Ranger reviewed the task as a general customer-success support request."
            recommendation = (
                "Clarify the customer, order or service context, desired outcome, risk level, and deadline. Recommend "
                "the next safest internal action first. Do not contact customers, publish, spend money, delete files, "
                "or make public-facing commitments without Manny approval when required."
            )

    return {
        "agent": "Ranger",
        "status": status,
        "task": task_text,
        "summary": summary,
        "recommendation": recommendation,
        "approval_required": approval_required,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }

if __name__ == "__main__":
    print(ranger_agent("Evaluate a 50 hat order at $19 each with $12 hat cost and $0.75 patch cost."))
