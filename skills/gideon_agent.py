from datetime import datetime


def gideon_agent(task):
    """
    Gideon Finance Agent worker for RAMFAM KINGDOM.

    Accepts:
        task (str): Finance-related task request.

    Returns:
        dict: Structured worker response.
    """
    if not isinstance(task, str):
        task = str(task)

    normalized_task = task.strip()
    task_lower = normalized_task.lower()

    approval_triggers = [
        "send",
        "publish",
        "post",
        "pay",
        "purchase",
        "buy",
        "spend",
        "refund",
        "charge",
        "invoice customer",
        "contact customer",
        "email customer",
        "message customer",
        "legal",
        "contract",
        "public",
        "announce",
        "delete",
        "remove file",
        "bank",
        "transfer",
        "withdraw",
        "deposit",
        "price change",
        "discount",
        "quote",
        "proposal",
        "customer-facing",
        "reputation",
    ]

    financial_terms = [
        "revenue",
        "cost",
        "profit",
        "margin",
        "invoice",
        "cash flow",
        "expense",
        "budget",
        "pricing",
        "receivable",
        "payable",
        "tax",
        "payroll",
        "forecast",
        "risk",
        "loss",
        "gain",
    ]

    approval_required = any(trigger in task_lower for trigger in approval_triggers)

    finance_related = any(term in task_lower for term in financial_terms)

    if not normalized_task:
        status = "needs_task"
        summary = "No task was provided for Gideon to review."
        recommendation = (
            "Provide a finance-related task involving revenue, cost, profit, "
            "invoices, cash flow, or financial risk."
        )
        approval_required = False
    elif finance_related:
        status = "review_ready"
        summary = (
            "Gideon reviewed the finance-related request for RAMFAM KINGDOM, "
            "SIS Custom Creations, FRESH Apparel, and ATLAS support."
        )

        if approval_required:
            recommendation = (
                "Prepare the financial review, identify risks, and present the "
                "recommended action to Manny for approval before taking any "
                "public, financial, customer-facing, legal, or reputation-impacting step."
            )
        else:
            recommendation = (
                "Analyze the numbers, summarize revenue, cost, profit, cash flow, "
                "and risk factors, then recommend the safest next action. No external "
                "action should be taken without approval if the recommendation becomes "
                "financial, public, customer-facing, legal, or reputation-impacting."
            )
    else:
        status = "limited_review"
        summary = (
            "The task does not clearly appear to be finance-related, but Gideon can "
            "still review it for financial risk and Kingdom impact."
        )

        if approval_required:
            recommendation = (
                "Do not execute the requested action. Review potential financial, "
                "customer, public, legal, or reputation impact and obtain Manny approval first."
            )
        else:
            recommendation = (
                "Clarify the financial objective, expected impact, and any risk to "
                "revenue, customer commitments, family stability, or Kingdom operations."
            )

    return {
        "agent": "Gideon",
        "status": status,
        "task": normalized_task,
        "summary": summary,
        "recommendation": recommendation,
        "approval_required": approval_required,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }

if __name__ == "__main__":
    print(gideon_agent("Evaluate a 50 hat order at $19 each with $12 hat cost and $0.75 patch cost."))
