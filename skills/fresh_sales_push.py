from datetime import datetime
import json
from pathlib import Path

MISSIONS_PATH = Path("agents/missions.json")
MISSIONS_PATH.parent.mkdir(exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")

missions = [
    {
        "agent": "Micah",
        "role": "Social Media Manager",
        "room": "Media Room",
        "status": "Working",
        "priority": "HIGH",
        "date": today,
        "mission": "Push FRESH Apparel today across Facebook, TikTok, Instagram, and community groups.",
        "task": "Create 3 short posts and 2 reel captions using Manny's Jimmy John's story, the Carolina blue shirt photo, and the hook: One Shirt = One Shirt + One Meal for someone in need.",
        "goal": "Drive traffic to the Shopify store and get at least 1 FRESH shirt sale today."
    },
    {
        "agent": "Amanda",
        "role": "Outreach + Marketplace Manager",
        "room": "Marketplace Room",
        "status": "Working",
        "priority": "HIGH",
        "date": today,
        "mission": "Push FRESH Apparel through personal outreach today.",
        "task": "Create 10 warm message templates Manny can send to friends, family, church contacts, local community members, and supporters.",
        "goal": "Start real conversations and ask for support without sounding spammy."
    }
]

if MISSIONS_PATH.exists():
    try:
        existing = json.loads(MISSIONS_PATH.read_text())
        if not isinstance(existing, list):
            existing = []
    except Exception:
        existing = []
else:
    existing = []

existing.extend(missions)

MISSIONS_PATH.write_text(json.dumps(existing, indent=2))

print("🔥 FRESH SALES PUSH ACTIVATED")
print("Micah is awake: Social media mission assigned.")
print("Amanda is awake: Outreach mission assigned.")
print("Goal: Sell FRESH TODAY.")