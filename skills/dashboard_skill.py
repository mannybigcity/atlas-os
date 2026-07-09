from skills.followup_skill import list_followups
from skills.proposal_skill import list_pending_proposals


def get_dashboard():
    followups = list_followups()
    pending_proposals = list_pending_proposals()

    dashboard = {
        "followup_count": len(followups),
        "followups": followups,
        "open_proposal_count": len(pending_proposals),
        "open_proposals": pending_proposals
    }

    return dashboard