# brain/intent_router.py

def detect_intent(text):
    text = text.lower().strip()

    conversation_phrases = [
        "i feel",
        "i'm feeling",
        "i am feeling",
        "i'm tired",
        "i am tired",
        "i'm frustrated",
        "i am frustrated",
        "let's talk",
        "real conversation",
        "can we talk",
        "what do you think",
        "slow",
        "very slow",
        "too slow",
        "you're slow",
        "you are slow",
        "response is slow",
        "respond faster",
        "speak faster",
        "human pace",
    ]

    for phrase in conversation_phrases:
        if phrase in text:
            return "conversation"

    return "command"


def is_conversation_followup(text):
    text = text.lower().strip()

    followups = [
        "slow",
        "very slow",
        "too slow",
        "faster",
        "yes",
        "no",
        "maybe",
        "kind of",
        "not really",
        "exactly",
        "right",
        "wrong",
    ]

    return text in followups
