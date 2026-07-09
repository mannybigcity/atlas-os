
from agents.atlas_orchestrator import atlas_orchestrator


def atlas_orchestrated_response(user_text: str, context: dict | None = None) -> dict:
    """
    Atlas Chief-of-Staff response gateway.
    Normal user messages come here first.
    Atlas decides whether to answer directly or delegate to the right agent.
    """
    context = context or {}

    result = atlas_orchestrator(user_text, context)

    return {
        "status": "success",
        "mode": "orchestrated",
        "user_text": user_text,
        "orchestrator_result": result,
    }
