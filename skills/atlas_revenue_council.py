from datetime import datetime
import json
from pathlib import Path

ROOT = Path(r"C:\Users\User\Desktop\PUTER")
BRAIN = ROOT / "RAMFAM_KINGDOM_BRAIN"
REPORTS = BRAIN / "06_MISSIONS"
REPORTS.mkdir(parents=True, exist_ok=True)

def atlas_revenue_council(prompt):
    prompt_lower = prompt.lower()

    opportunities = [
        {
            "name": "AI short-form video service",
            "target": "Realtors, HVAC, roofers, churches, local service businesses",
            "offer": "3 AI reels for $99 or 12 reels/month for $299",
            "why_now": "Businesses need content but hate making it.",
            "today_action": "Message 10 local business owners with a sample offer."
        },
        {
            "name": "UGC-style local business promos",
            "target": "Restaurants, barbers, salons, gyms, boutiques",
            "offer": "Simple phone-recorded testimonial/ad package for $75-$150",
            "why_now": "Small businesses want authentic content more than polished ads.",
            "today_action": "Post one Facebook offer and DM 10 businesses."
        },
        {
            "name": "AI lead list + outreach starter pack",
            "target": "Pressure washers, cleaners, mobile detailers, lawn care, roofers",
            "offer": "50 local leads + 3 outreach scripts for $49-$99",
            "why_now": "Service businesses need customers immediately.",
            "today_action": "Build one sample list and offer it in local groups."
        }
    ]

    report = {
        "mission": "Atlas Revenue Council",
        "prompt": prompt,
        "timestamp": datetime.now().isoformat(),
        "agents": {
            "Hunter": "Best immediate money path: sell simple digital marketing help, not full software.",
            "Scout": "Focus on local service businesses already spending money or needing leads.",
            "Amanda": "Use direct, friendly outreach. Offer a small starter package today.",
            "David": "Track every prospect in a simple CSV: name, business, contact, offer, status, next follow-up.",
            "Atlas": "Recommended move: start with AI short-form video service because it matches your existing vision and can become recurring revenue."
        },
        "top_recommendation": opportunities[0],
        "backup_options": opportunities[1:],
        "manny_action_plan_today": [
            "Pick one offer only: 3 AI reels for $99.",
            "Create one sample reel concept for a realtor or local service business.",
            "DM or text 10 people today.",
            "Track replies in CRM Importer or a simple CSV.",
            "Do not build more features until 10 offers are sent."
        ],
        "approval_required": True
    }

    latest = REPORTS / "revenue_council_latest.json"
    archive = REPORTS / f"revenue_council_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    latest.write_text(json.dumps(report, indent=2), encoding="utf-8")
    archive.write_text(json.dumps(report, indent=2), encoding="utf-8")

    return report

if __name__ == "__main__":
    result = atlas_revenue_council("Find ways Manny can make money today with digital marketing, UGC, AI content, or local outreach.")
    print(json.dumps(result, indent=2))
