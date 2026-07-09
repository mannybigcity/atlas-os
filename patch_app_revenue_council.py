from pathlib import Path

app = Path("app.py")
text = app.read_text(encoding="utf-8")

block = '''    elif intent == "revenue_council":
        response = atlas_delegate(user_message)

'''

if 'intent == "revenue_council"' not in text:
    text = text.replace(
        '    elif intent == "executive_briefing":\n',
        block + '    elif intent == "executive_briefing":\n'
    )

app.write_text(text, encoding="utf-8")
print("app.py patched for Revenue Council")
