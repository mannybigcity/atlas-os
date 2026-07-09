# skills/gideon_deliverable.py


def generate_gideon_deliverables():
    money_report_task = """🐂 GIDEON DELIVERABLE

MONEY REPORT TASK

Gideon, review all orders, invoices, and revenue records.

Report:
- Paid money
- Outstanding money
- Next money target
- Awaiting payment orders
- Total pipeline
"""

    invoice_message = """INVOICE MESSAGE

Hi!

Thank you again for the opportunity to help with your project.

Your invoice has been sent over.

Once payment is completed, we can move forward with the next step.

Please let me know if you have any questions.
"""

    payment_reminder = """PAYMENT REMINDER

Hi!

Just wanted to send a friendly reminder regarding the outstanding balance.

Please let me know if you need another copy of the invoice.

Thank you!
"""

    daily_money_briefing = """DAILY MONEY BRIEFING

Gideon, give Manny a simple money report:

1. What money has been paid?
2. What money is still outstanding?
3. Who should be followed up with first?
4. What is the next closest payment?
5. What should Manny do today to move money forward?
"""

    return "\n\n".join([
        money_report_task,
        invoice_message,
        payment_reminder,
        daily_money_briefing
    ])