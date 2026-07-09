from dataclasses import dataclass


@dataclass
class KingdomOption:
    name: str
    revenue: int = 0
    customer: int = 0
    stability: int = 0
    system: int = 0
    expansion: int = 0

    @property
    def total_score(self) -> int:
        return (
            self.revenue
            + self.customer
            + self.stability
            + self.system
            + self.expansion
        )


def score_option(option_text: str) -> KingdomOption:
    text = option_text.lower()

    option = KingdomOption(name=option_text)

    revenue_words = ["invoice", "paid", "payment", "quote", "sale", "customer", "prospect", "follow up", "lead"]
    customer_words = ["order", "customer", "bobbie", "kandy", "ray", "artwork", "delivery", "shirt", "hat"]
    stability_words = ["bill", "cash", "money", "rent", "expense", "utilities", "probation", "family"]
    system_words = ["system", "code", "atlas", "puter", "automation", "crm", "dashboard", "process"]
    expansion_words = ["new", "idea", "agent", "website", "project", "shepnav", "fresh"]

    option.revenue = sum(2 for word in revenue_words if word in text)
    option.customer = sum(2 for word in customer_words if word in text)
    option.stability = sum(2 for word in stability_words if word in text)
    option.system = sum(2 for word in system_words if word in text)
    option.expansion = sum(1 for word in expansion_words if word in text)

    return option


def rank_kingdom_options(options: list[str]) -> list[KingdomOption]:
    scored = [score_option(option) for option in options]

    return sorted(
        scored,
        key=lambda item: (
            item.total_score,
            item.revenue,
            item.customer,
            item.stability,
            item.system,
            -item.expansion,
        ),
        reverse=True,
    )


def build_decision_report(options: list[str]) -> str:
    ranked = rank_kingdom_options(options)

    lines = []
    lines.append("[ATLAS DECISION ENGINE]")
    lines.append("")
    lines.append("Kingdom Laws Applied:")
    lines.append("- Revenue Before Expansion")
    lines.append("- Systems Before Scale")
    lines.append("- Protect The King's Focus")
    lines.append("- Customer Commitments Before New Opportunities")
    lines.append("")

    lines.append("Ranked Priorities:")
    lines.append("")

    for index, option in enumerate(ranked, start=1):
        lines.append(f"{index}. {option.name}")
        lines.append(f"   Total Score: {option.total_score}")
        lines.append(f"   Revenue: {option.revenue}")
        lines.append(f"   Customer: {option.customer}")
        lines.append(f"   Stability: {option.stability}")
        lines.append(f"   System: {option.system}")
        lines.append(f"   Expansion: {option.expansion}")
        lines.append("")

    if ranked:
        top = ranked[0]
        lines.append("Atlas Recommendation:")
        lines.append(f"Work on this first: {top.name}")
        lines.append("")
        lines.append("Reason:")
        lines.append("This option scored highest under the Kingdom priority system.")
        lines.append("")
        lines.append("Next Action:")
        lines.append("Take one small step on this item now.")

    return "\n".join(lines)


if __name__ == "__main__":
    test_options = [
        "Follow up with Uncle Ray about unpaid invoice",
        "Build Amanda outreach agent",
        "Work on FRESH Apparel website idea",
        "Check Bobbie B&B HVAC customer order",
        "Improve Atlas decision system",
    ]

    print(build_decision_report(test_options))