from datetime import datetime
from pathlib import Path
import sys

PROJECT_ROOT = Path(r"C:\Users\User\Desktop\PUTER")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents import atlas_agent_delegation

VALID_AGENTS = {
    "mason",
    "hunter",
    "gideon",
    "david",
    "amanda",
    "ranger",
    "scout",
    "micah",
    "taylor",
}

ATLAS_ALLOWED_WRITE_LOCATIONS = [
    r"C:\Users\User\Desktop\PUTER",
    r"C:\Users\User\Desktop\PUTER\RAMFAM_KINGDOM_BRAIN",
]


def _is_atlas_self_question(user_text):
    text = (user_text or "").lower()
    identity_markers = [
        "who are you",
        "what are your authority rules",
        "authority rules",
        "allowed write locations",
        "write locations",
    ]
    return any(marker in text for marker in identity_markers)


def _atlas_self_report():
    return {
        "status": "answered_by_atlas",
        "agent": "Atlas",
        "identity": "Atlas is the Golden Lion and Chief of Staff of the RAMFAM Kingdom.",
        "role": "Atlas coordinates Kingdom agents, delegates to specialists, reviews findings, prioritizes action, and gives Manny final recommendations.",
        "authority_rules": [
            "Manny is the final authority.",
            "Atlas does not override Manny.",
            "Manny approval is required before public actions.",
            "Manny approval is required before financial commitments.",
            "Manny approval is required before customer-facing actions.",
            "Manny approval is required before legal actions.",
            "Manny approval is required before reputation-impacting actions.",
        ],
        "allowed_write_locations": ATLAS_ALLOWED_WRITE_LOCATIONS,
        "write_policy": "Atlas should coordinate and delegate most build/write work to Mason. Direct writes stay inside PUTER/RAMFAM_KINGDOM_BRAIN unless Manny explicitly approves otherwise.",
        "approval_required": False,
    }


ROUTE_RULES = [
    (
        "taylor",
        ["website", "landing page", "page copy"],
        "Taylor handles website, landing page, and page copy work.",
    ),
    (
        "ranger",
        ["customer issue", "retention", "satisfaction"],
        "Ranger handles customer issues, retention, and satisfaction.",
    ),
    (
        "david",
        ["follow-up", "follow up", "crm", "customers", "customer"],
        "David handles follow-up, CRM, and customer tracking.",
    ),
    (
        "hunter",
        ["leads", "lead", "opportunities", "opportunity", "revenue", "prospects", "prospect"],
        "Hunter handles leads, opportunities, revenue, and prospects.",
    ),
    (
        "gideon",
        ["profit", "margin", "cash flow", "cost"],
        "Gideon handles profit, margin, cash flow, and cost.",
    ),
    (
        "amanda",
        ["outreach", "message", "partnership", "marketplace"],
        "Amanda handles outreach, messages, partnerships, and marketplace work.",
    ),
    (
        "scout",
        ["research", "find info", "intelligence"],
        "Scout handles research, finding information, and intelligence.",
    ),
    (
        "micah",
        ["post", "caption", "social media", "content"],
        "Micah handles posts, captions, social media, and content.",
    ),
    (
        "mason",
        [
            "build",
            "create file",
            "fix code",
            "inspect code",
            "run test",
            "run tests",
            "verify",
            "improve system",
            "system improvement",
            "system improvements",
            "operating system better",
        ],
        "Mason handles builds, files, code, tests, verification, and system improvement.",
    ),
]


def _normalize_context(context):
    if context is None:
        return {}
    if not isinstance(context, dict):
        return {"context": context}
    return dict(context)


def _detect_agent(user_text, context=None):
    context = _normalize_context(context)
    requested_agent = str(context.get("agent", "")).strip().lower()
    if requested_agent in VALID_AGENTS:
        return requested_agent, f"{requested_agent.title()} selected by context override."

    text = (user_text or "").lower()
    for named_agent in VALID_AGENTS:
        if named_agent in text:
            return named_agent, f"{named_agent.title()} selected because Manny named the agent directly."
    for agent, keywords, reason in ROUTE_RULES:
        for keyword in keywords:
            if keyword in text:
                return agent, f"{agent.title()} selected because request matched keyword '{keyword}'. {reason}"

    return "mason", "Mason selected by default because Atlas system requests should route to the Kingdom Architect when no specialized route matches."


def atlas_orchestrator(user_text, context=None):
    """
    Route an Atlas request to the right Kingdom agent without requiring the user
    to say, "Atlas, have [agent]...".

    Returns:
        dict with routed_to, reason, result, and timestamp.
    """
    if _is_atlas_self_question(user_text):
        return {
            "routed_to": "Atlas",
            "reason": "Atlas answered directly because this was an Atlas identity, authority, or write-location question.",
            "result": _atlas_self_report(),
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }

    delegation_context = _normalize_context(context)
    agent, reason = _detect_agent(user_text, delegation_context)
    delegation_context["agent"] = agent

    result = atlas_agent_delegation.delegate_to_agent(user_text, delegation_context)

    return {
        "routed_to": agent.title(),
        "reason": reason,
        "result": result,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }


if __name__ == "__main__":
    print(atlas_orchestrator("Please build and verify the system", {"execute_now": False}))
