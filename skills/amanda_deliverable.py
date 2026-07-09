# skills/amanda_deliverable.py


def generate_amanda_deliverables():
    school_outreach = """🐼 AMANDA DELIVERABLE

SCHOOL / DAYCARE OUTREACH MESSAGE

Hi! My name is Manny with SIS Custom Creations.

We offer mobile kids' paint and splatter paint parties for schools, daycares, birthdays, and community events.

Our kids paint parties start at $12 per child with a 10 child minimum.

We bring the creative fun to you.

If your school or daycare ever needs a fun activity, summer event, birthday add-on, or creative party option, I’d love to send you more info.

Thank you!
"""

    facebook_group_post = """FACEBOOK GROUP POST

Hey Cypress / Northwest Houston families!

My wife and I run SIS Custom Creations, and we offer mobile kids' paint and splatter paint parties.

Great for:
- Birthday parties
- Daycares
- Summer activities
- Church events
- School fun days
- Community events

Kids paint parties start at $12 per child with a 10 child minimum.

We bring the creative fun to you.

Message me if you’d like details!
"""

    daycare_call_script = """DAYCARE CALL SCRIPT

Hi, my name is Manny with SIS Custom Creations.

I wanted to ask who I could speak with about kids' activities or summer events.

We offer mobile paint and splatter paint parties for daycares, schools, and birthday events.

Our kids parties start at $12 per child with a 10 child minimum, and we bring the activity to you.

What would be the best email to send information to?
"""

    lead_list_prompt = """LEAD LIST TASK

Amanda, find 10 schools, daycares, churches, or community groups in Cypress, Tomboll, Waller, Jersey Village, Spring, and Northwest Houston that may be good fits for SIS Custom Creations mobile paint parties.

For each lead, collect:
- Business / organization name
- Contact person if available
- Phone number
- Email
- Website or Facebook page
- City
- Notes
"""

    return "\n\n".join([
        
        school_outreach,
        facebook_group_post,
        daycare_call_script,
        lead_list_prompt
    ])