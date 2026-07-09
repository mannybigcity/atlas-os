from pathlib import Path

router = Path(r"C:\Users\User\Desktop\PUTER\agents\atlas_delegation_router.py")
text = router.read_text(encoding="utf-8")

# 1. Add Revenue Council import if missing
import_line = "from skills.atlas_revenue_council import atlas_revenue_council"
if import_line not in text:
    text = text.replace(
        "from skills.atlas_strategic_command import atlas_strategic_command\n",
        "from skills.atlas_strategic_command import atlas_strategic_command\n"
        "from skills.atlas_revenue_council import atlas_revenue_council\n"
    )

# 2. Add classifier route before generic task/hermes routing
route_block = '''    if (
        "revenue council" in message
        or "make money" in message
        or "money today" in message
        or "digital marketing" in message
        or "ugc" in message
        or "find ways to make money" in message
    ):
        return "revenue_council"

'''
if 'return "revenue_council"' not in text:
    marker = "    task_words = [\n"
    text = text.replace(marker, route_block + marker)

# 3. Add delegate handler before strategic command handler
handler_block = '''    if route == "revenue_council":
        report = atlas_revenue_council(user_message)
        top = report.get("top_recommendation", {})
        agents = report.get("agents", {})
        actions = report.get("manny_action_plan_today", [])

        response = "Atlas Revenue Council is active.\\n\\n"
        response += "Hunter: " + agents.get("Hunter", "") + "\\n"
        response += "Scout: " + agents.get("Scout", "") + "\\n"
        response += "Amanda: " + agents.get("Amanda", "") + "\\n"
        response += "David: " + agents.get("David", "") + "\\n\\n"
        response += "Atlas Recommendation:\\n"
        response += f"{top.get('name', 'Opportunity')} — {top.get('offer', '')}\\n"
        response += f"Target: {top.get('target', '')}\\n"
        response += f"Why now: {top.get('why_now', '')}\\n\\n"
        response += "Manny Action Plan Today:\\n"
        for index, action in enumerate(actions, start=1):
            response += f"{index}. {action}\\n"
        response += "\\nApproval required before outreach is sent."
        return response

'''
if 'if route == "revenue_council":' not in text:
    marker = "    if route == \"atlas_strategic_command\":\n"
    text = text.replace(marker, handler_block + marker)

router.write_text(text, encoding="utf-8")
print("Revenue Council patched into atlas_delegation_router.py")
