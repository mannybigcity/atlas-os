# atlas_intent_router.py
# RAMFAM KINGDOM - ATLAS INTENT ROUTER

def _is_memory_lookup(msg: str) -> bool:
    """Return True when a normal chat message should consult Atlas 99_MEMORY."""
    availability_phrases = [
        "who is available",
        "who's available",
        "who is on standby",
        "who's on standby",
        "available agents",
        "standby agents",
    ]
    if any(phrase in msg for phrase in availability_phrases):
        return False

    memory_triggers = [
        "what do you remember",
        "do you remember",
        "what do you know about",
        "who is my",
        "who's my",
        "who am i",
        "tell me about me",
        "tell me about my",
        "remember about",
        "why does atlas exist",
        "why atlas exists",
        "my wife",
        "my daughter",
        "my son",
        "granddaughter",
        "nickname",
        "birthday",
        "current goal",
        "sis believe",
        "family",
    ]
    return any(trigger in msg for trigger in memory_triggers)


def route_intent(user_message: str) -> dict:
    msg = (user_message or "").lower().strip()

    direct_triggers = [
        "say the kingdom is operational",
        "kingdom is operational",
        "are you online",
        "atlas online",
        "atlas status",
        "say hello",
        "hello atlas",
    ]

    if any(trigger in msg for trigger in direct_triggers):
        return {
            "intent": "direct",
            "response": "The Kingdom is operational. ATLAS is online."
        }

    revenue_triggers = [
        "revenue council",
        "money council",
        "make money",
        "money today",
        "digital marketing",
        "ugc",
        "business opportunity",
        "opportunity finder",
        "find ways to make money",
        "make money today",
        "ways to make money",
    ]

    if any(trigger in msg for trigger in revenue_triggers):
        return {"intent": "revenue_council", "response": None}

    if "morning briefing" in msg or "executive briefing" in msg or "daily briefing" in msg:
        return {"intent": "executive_briefing", "response": None}

    if "full briefing" in msg or "expand" in msg or "deep dive" in msg:
        return {"intent": "expand", "response": None}

    scripture_triggers = [
        "verse of the day",
        "scripture",
        "morning reading",
        "devotional",
        "proverbs",
        "psalm",
        "bible verse"
    ]

    if any(trigger in msg for trigger in scripture_triggers):
        return {"intent": "scripture", "response": None}

    if _is_memory_lookup(msg):
        return {"intent": "retrieval", "response": None}

    retrieval_triggers = [
        "show file",
        "open file",
        "read file",
        "kingdom laws",
        "agent roles",
        "atlas identity",
        "mason file",
        "amanda file",
        "gideon file",
        "hunter file",
        "micah file",
        "ranger file",
        "david file",
    ]

    if any(trigger in msg for trigger in retrieval_triggers):
        return {"intent": "retrieval", "response": None}

    hermes_triggers = [
        "build",
        "create code",
        "fix code",
        "refactor",
        "analyze this code",
        "website",
        "html",
        "css",
        "javascript",
        "python",
        "flask"
    ]

    if any(trigger in msg for trigger in hermes_triggers):
        return {"intent": "hermes", "response": None}

    return {"intent": "chat", "response": None}
