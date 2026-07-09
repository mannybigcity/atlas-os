from datetime import datetime


def scout_agent(task):
    task_text = str(task or "").strip()
    task_lower = task_text.lower()

    approval_keywords = [
        "public",
        "publish",
        "post",
        "social media",
        "advertise",
        "ad",
        "paid",
        "spend",
        "buy",
        "purchase",
        "order",
        "invoice",
        "quote",
        "pricing",
        "price",
        "financial",
        "money",
        "customer",
        "client",
        "lead contact",
        "contact",
        "email",
        "call",
        "text",
        "sms",
        "message",
        "legal",
        "contract",
        "agreement",
        "reputation",
        "review",
        "complaint",
        "refund",
        "discount",
        "commitment",
    ]

    approval_required = any(keyword in task_lower for keyword in approval_keywords)

    if not task_text:
        status = "needs_task"
        summary = "Scout did not receive a research task."
        recommendation = "Provide a clear research target such as leads, companies, opportunities, tools, competitors, or useful information for RAMFAM Kingdom."
        approval_required = False
    else:
        status = "ready"
        summary = (
            "Scout can research and organize useful information for RAMFAM Kingdom, "
            "SIS Custom Creations, FRESH Apparel, and ATLAS without using external APIs, "
            "sending messages, spending money, deleting files, or taking public action."
        )

        if approval_required:
            recommendation = (
                "Prepare findings, options, risks, and a recommended next step, then request Manny approval before taking any public, financial, customer-facing, legal, or reputation-impacting action."
            )
        else:
            recommendation = (
                "Gather practical information, identify useful opportunities, summarize the best options, and recommend the next safe internal action."
            )

    return {
        "agent": "Scout",
        "status": status,
        "task": task_text,
        "summary": summary,
        "recommendation": recommendation,
        "approval_required": approval_required,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }

if __name__ == "__main__":
    print(scout_agent("Evaluate a 50 hat order at $19 each with $12 hat cost and $0.75 patch cost."))
