from crm.crm_skill import load_prospects

def filter_prospects_by_status(status):
    prospects = load_prospects()

    matches = [
        prospect for prospect in prospects
        if prospect["status"].lower() == status.lower()
    ]

    if not matches:
        return f"No prospects found with status: {status}"

    lines = []
    for p in matches:
        lines.append(
            f"{p['name']} | {p['business']} | {p['product']} | {p['status']}"
        )

    return "\n".join(lines)