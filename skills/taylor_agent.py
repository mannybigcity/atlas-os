from datetime import datetime


def taylor_agent(task):
    """
    Taylor: RAMFAM KINGDOM Website Builder Agent.

    Designs website concepts, page structures, copy ideas, UI recommendations,
    and future web inspiration for RAMFAM KINGDOM, SIS Custom Creations,
    FRESH Apparel & Design, PUTER, and ATLAS support.

    This worker does not send messages, publish posts, spend money, contact
    customers, delete files, or use external APIs.
    """
    if not isinstance(task, str):
        task = str(task)

    clean_task = task.strip()

    approval_keywords = [
        "publish",
        "go live",
        "launch",
        "public",
        "customer",
        "client",
        "checkout",
        "payment",
        "invoice",
        "pricing",
        "price",
        "discount",
        "sale",
        "refund",
        "legal",
        "terms",
        "privacy",
        "policy",
        "contract",
        "claim",
        "guarantee",
        "testimonial",
        "review",
        "brand statement",
        "press",
        "reputation",
        "ad",
        "advertisement",
        "campaign",
        "email customers",
        "contact customers",
        "domain",
        "seo title",
        "meta description",
    ]

    approval_required = any(
        keyword in clean_task.lower() for keyword in approval_keywords
    )

    if not clean_task:
        status = "needs_task"
        summary = (
            "Taylor did not receive a usable website-building task. "
            "A clear request is needed before page structure, copy, or UI "
            "recommendations can be prepared."
        )
        recommendation = (
            "Provide a specific website task, such as creating a homepage outline, "
            "improving service page copy, planning a landing page, or drafting a "
            "website section for SIS Custom Creations, FRESH Apparel, PUTER, or "
            "RAMFAM KINGDOM."
        )
    else:
        status = "ready"
        summary = (
            "Taylor reviewed the website-related task and can support it with "
            "practical page structure, copy direction, user experience ideas, "
            "and implementation-ready recommendations while staying within safe "
            "RAMFAM KINGDOM operating rules."
        )

        recommendation_parts = [
            "Clarify the intended audience and business goal before building.",
            "Create a simple page structure with a clear headline, supporting copy, trust-building proof, and a direct call to action.",
            "Keep the design clean, mobile-friendly, fast-loading, and aligned with the RAMFAM KINGDOM brand family.",
            "Use real business details and approved assets instead of placeholders whenever possible.",
            "Prepare the work for review before anything public, financial, customer-facing, legal, or reputation-impacting is released.",
        ]

        if "sis" in clean_task.lower() or "custom" in clean_task.lower():
            recommendation_parts.append(
                "For SIS Custom Creations, emphasize custom apparel, hats, laser engraving, promotional products, event services, signs, quality, turnaround, and easy quote requests."
            )

        if "fresh" in clean_task.lower() or "apparel" in clean_task.lower():
            recommendation_parts.append(
                "For FRESH Apparel & Design, highlight the mission: Faithfully Reaching Everybody Seeking Hope, with clear product storytelling and the One Shirt. One Meal. impact message."
            )

        if "puter" in clean_task.lower() or "atlas" in clean_task.lower():
            recommendation_parts.append(
                "For PUTER or ATLAS, focus on operational clarity, agent support, dashboards, workflows, and reducing friction for the King's focus."
            )

        recommendation = " ".join(recommendation_parts)

    if approval_required:
        recommendation += (
            " Manny approval is required before taking this action because it may "
            "affect public presence, finances, customers, legal obligations, or "
            "brand reputation."
        )

    return {
        "agent": "Taylor",
        "status": status,
        "task": clean_task,
        "summary": summary,
        "recommendation": recommendation,
        "approval_required": approval_required,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }

if __name__ == "__main__":
    print(taylor_agent("Evaluate a 50 hat order at $19 each with $12 hat cost and $0.75 patch cost."))
