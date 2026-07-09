import json, time
from pathlib import Path
from datetime import datetime

BUS = Path(r"C:\Users\User\Desktop\PUTER\atlas_os\communications\executive_messages.json")

while True:
    print("\033c", end="")
    print("ATLAS MISSION CONTROL - EXECUTIVE TEAM LIVE")
    print("Updated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)

    try:
        messages = json.loads(BUS.read_text(encoding="utf-8-sig"))
    except Exception as e:
        print("Could not read executive bus:", e)
        messages = []

    for msg in messages[-20:]:
        print(f"[{msg.get('status','')}] {msg.get('from')} -> {msg.get('to')}")
        print(f"Mission: {msg.get('mission_id')}")
        print(f"Title: {msg.get('title')}")
        print(f"Next: {msg.get('next_action')}")
        print("-" * 60)

    time.sleep(5)
