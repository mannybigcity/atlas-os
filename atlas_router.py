def detect_intent(message):
    text = (message or "").lower().strip()

    conversational_keywords = [
        "how are you",
        "good morning",
        "good night",
        "hello",
        "hey atlas",
        "talk to me",
        "conversation",
        "real conversation",
        "what do you think",
        "what should we work on",
        "help me think"
    ]

    brain_keywords = [
        "kingdom laws",
        "agent roles",
        "hunter",
        "mason",
        "gideon",
        "amanda",
        "micah",
        "ranger",
        "scout",
        "constitution",
        "preamble",
        "invoice",
        "morning briefing",
        "brain status"
    ]

    builder_keywords = [
        "build",
        "code",
        "fix",
        "python",
        "flask",
        "html",
        "router",
        "app.py",
        "dashboard"
    ]

    if any(k in text for k in conversational_keywords):
        return {
            "intent": "conversation",
            "use_brain": False,
            "use_hermes": False,
            "mode": "advisor"
        }

    if any(k in text for k in builder_keywords):
        return {
            "intent": "builder",
            "use_brain": False,
            "use_hermes": True,
            "mode": "builder"
        }

    if any(k in text for k in brain_keywords):
        return {
            "intent": "brain_lookup",
            "use_brain": True,
            "use_hermes": False,
            "mode": "brief"
        }

    return {
        "intent": "general",
        "use_brain": False,
        "use_hermes": False,
        "mode": "advisor"
    }


def atlas_router_response(message):
    route = detect_intent(message)

    if route["use_brain"]:
        return None

    if route["intent"] == "conversation":
        return (
            "I hear you. I do not need to search the Kingdom Brain for this. "
            "Lets talk plainly. You want a real conversation, not a file dump. "
            "I will answer like your Chief of Staff."
        )

    if route["intent"] == "builder":
        return (
            "Builder Mode activated. I will help build this one brick at a time."
        )

    return (
        "I understand. I do not need to search the Kingdom Brain for this."
    )
