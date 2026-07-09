from pathlib import Path

app = Path("app.py")
text = app.read_text(encoding="utf-8")

if "from skills.atlas_revenue_council import atlas_revenue_council" not in text:
    text = text.replace(
        "from agents.atlas_delegation_router import atlas_delegate\n",
        "from agents.atlas_delegation_router import atlas_delegate\n"
        "from skills.atlas_revenue_council import atlas_revenue_council\n"
    )

old = '''    elif intent == "revenue_council":
        response = atlas_delegate(user_message)

'''

new = '''    elif intent == "revenue_council":
        report = atlas_revenue_council(user_message)
        top = report.get("top_recommendation", {})
        agents = report.get("agents", {})
        actions = report.get("manny_action_plan_today", [])

        response = "ATLAS REVENUE COUNCIL ACTIVE\\n\\n"
        response += "Hunter: " + agents.get("Hunter", "") + "\\n"
        response += "Scout: " + agents.get("Scout", "") + "\\n"
        response += "Amanda: " + agents.get("Amanda", "") + "\\n"
        response += "David: " + agents.get("David", "") + "\\n\\n"
        response += "Atlas Recommendation:\\n"
        response += top.get("name", "Opportunity") + " - " + top.get("offer", "") + "\\n"
        response += "Target: " + top.get("target", "") + "\\n"
        response += "Why now: " + top.get("why_now", "") + "\\n\\n"
        response += "Manny Action Plan Today:\\n"
        for index, action in enumerate(actions, start=1):
            response += str(index) + ". " + action + "\\n"

'''

text = text.replace(old, new)
app.write_text(text, encoding="utf-8")
print("app.py Revenue Council direct skill patch complete")
