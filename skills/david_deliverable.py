# skills/david_deliverable.py


def generate_david_deliverables():
    followup_1 = """🐺 DAVID DELIVERABLE

FOLLOW-UP MESSAGE #1

Hey, just checking in to see if you had a chance to review the quote.

Let me know if you have any questions. I'd love to help get your project moving forward.

Thank you!
"""

    followup_2 = """FOLLOW-UP MESSAGE #2

Just wanted to touch base regarding your order.

We're ready whenever you are.

If you'd like to move forward, simply reply and we'll get everything started.
"""

    invoice_followup = """INVOICE FOLLOW-UP

Hi!

I wanted to follow up regarding the invoice that was sent.

Please let me know if you need another copy or if there are any questions.

Thank you for the opportunity to earn your business.
"""

    prospect_review = """PROSPECT REVIEW TASK

David, review all prospects and identify:

- Who needs follow-up
- Who has an outstanding invoice
- Who has approved a mockup
- Who is closest to becoming revenue

Rank them from hottest to coldest.
"""

    return "\n\n".join([
        followup_1,
        followup_2,
        invoice_followup,
        prospect_review
    ])