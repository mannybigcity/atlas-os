from datetime import datetime

ATLAS_GOVERNANCE = {
    "first_law": "Massive Action. Maximum Effort. Minimal Money.",
    "manny_final_authority": True,
    "do_not_rebuild_existing_functionality": True,
    "approval_required_for": [
        "public actions",
        "financial commitments",
        "customer-facing actions",
        "legal actions",
        "reputation-impacting actions",
        "expensive AI/token usage"
    ],
    "default_build_agent": "Mason",
    "default_rule": "Inspect existing files before creating new systems."
}

def governance_check(action, estimated_cost=0):
    needs_approval = estimated_cost > 0.25
    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "action": action,
        "approved_to_continue": not needs_approval,
        "approval_required": needs_approval,
        "estimated_cost": estimated_cost,
        "governance": ATLAS_GOVERNANCE
    }

if __name__ == "__main__":
    print(governance_check("Atlas OS governance installed", 0))
