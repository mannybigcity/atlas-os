# brain/decision_engine.py

def evaluate(options):

    if not options:
        return None

    highest_score = max(options, key=lambda x: x.get("score", 0))

    return highest_score