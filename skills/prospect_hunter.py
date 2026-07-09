# skills/prospect_hunter.py


def generate_prospect_hunter_report():
    mission = """🎯 PROSPECT HUNTER

MISSION

Find opportunities that can become money.

Priority Targets:

1. Schools
2. Daycares
3. Churches
4. Local Businesses
5. Sports Teams
6. Community Groups

Goal:
Generate conversations that can become quotes, invoices, and paid orders.
"""

    school_hunt = """SCHOOL HUNT

Look for:

- Elementary schools
- Private schools
- Daycares
- Summer camps

Offer:

- Paint parties
- Splatter paint parties
- Spirit shirts
- Teacher gifts
- Fundraisers
"""

    business_hunt = """BUSINESS HUNT

Look for:

- HVAC companies
- Plumbing companies
- Electricians
- Roofing companies
- Landscaping companies

Offer:

- Company shirts
- Hats
- Signs
- Promotional items
"""

    sports_hunt = """SPORTS HUNT

Look for:

- Baseball teams
- Softball teams
- Football teams
- Soccer teams
- Cheer organizations

Offer:

- Team shirts
- Parent shirts
- Coach gifts
- Banners
"""

    daily_assignment = """DAILY ASSIGNMENT

Find 10 prospects.

For each prospect collect:

- Name
- Business
- Contact
- Phone
- Email
- Website
- Notes

Rank:
Hot
Warm
Cold
"""

    return "\n\n".join([
        mission,
        school_hunt,
        business_hunt,
        sports_hunt,
        daily_assignment
    ])