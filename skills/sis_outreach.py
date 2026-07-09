# skills/sis_outreach.py


def generate_sis_outreach_report():
    mission = """🎨 SIS OUTREACH

MISSION

Grow SIS Custom Creations through community outreach.

Primary Services:

- Paint Parties
- Splatter Paint Parties
- Shirts
- Hats
- Signs
- Laser Engraving
"""

    school_strategy = """SCHOOL STRATEGY

Target:

- Elementary Schools
- Middle Schools
- PTO Groups
- Summer Programs

Offer:

- Paint Parties
- Spirit Wear
- Teacher Appreciation Gifts
- Fundraisers
"""

    daycare_strategy = """DAYCARE STRATEGY

Target:

- Private Daycares
- Church Daycares
- Learning Centers

Offer:

- Mobile Paint Parties
- Summer Activities
- Holiday Events
- Parent Appreciation Gifts
"""

    church_strategy = """CHURCH STRATEGY

Target:

- Children's Ministries
- Youth Ministries
- Vacation Bible School
- Community Events

Offer:

- Paint Activities
- Event Shirts
- Signs
- Fundraisers
"""

    daily_assignment = """DAILY ASSIGNMENT

Contact:

- 5 Schools
- 5 Daycares
- 2 Churches

Collect:

- Contact Name
- Phone Number
- Email
- Website
- Notes

Goal:

Create conversations.
Schedule meetings.
Generate quotes.
"""

    return "\n\n".join([
        mission,
        school_strategy,
        daycare_strategy,
        church_strategy,
        daily_assignment
    ])