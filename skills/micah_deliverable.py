# skills/micah_deliverable.py


def micah_facebook_post():
    return """🦊 MICAH DELIVERABLE

FACEBOOK POST

Today something small happened that confirmed the mission.

I stopped at Jimmy John's after my doctor's appointment, and an older gentleman walked up to me and said, "Hey, I really like your shirt."

He had no idea how much that meant to me.

FRESH Apparel & Design is more than a shirt brand.

FRESH stands for:
Faithfully Reaching Every Body Seeking Hope.

Every FRESH shirt helps provide a shirt and a meal to someone in need.

One Shirt. One Meal. One Person Helped.

If you want to support the mission, grab a FRESH shirt today.

#FRESH #FaithInAction #OneShirtOneMeal #HoustonSmallBusiness
"""


def generate_micah_deliverables():
    reel_caption_1 = """REEL CAPTION 1

A stranger stopped me today and said he liked my shirt.

He had no idea what that shirt represents.

FRESH Apparel & Design
Faithfully Reaching Every Body Seeking Hope.

One Shirt. One Meal. One Person Helped.

#FRESH #FaithInAction #OneShirtOneMeal
"""

    reel_caption_2 = """REEL CAPTION 2

This shirt is bigger than fashion.

Every FRESH shirt helps provide a shirt and a meal to someone in need.

One Shirt. One Meal. One Person Helped.

FRESH Apparel & Design
Faithfully Reaching Every Body Seeking Hope.
"""

    community_post = """COMMUNITY POST

Hey Cypress family,

I recently launched FRESH Apparel & Design, a faith-based apparel brand with a mission.

FRESH stands for Faithfully Reaching Every Body Seeking Hope.

Every shirt purchased helps provide a shirt and a meal to someone in need.

One Shirt. One Meal. One Person Helped.

If you’d like to support a local small business with a purpose, check out FRESH Apparel & Design.

Thank you for supporting local.
"""

    dm_script = """DM SCRIPT

Hey! I just launched FRESH Apparel & Design.

It’s a faith-based shirt brand with a mission:
Every shirt helps provide a shirt and a meal to someone in need.

FRESH stands for Faithfully Reaching Every Body Seeking Hope.

No pressure at all, but if you want to support the mission, I’d be grateful.

One Shirt. One Meal. One Person Helped.
"""

    return "\n\n".join([
        micah_facebook_post(),
        reel_caption_1,
        reel_caption_2,
        community_post,
        dm_script
    ])
