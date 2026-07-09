def operations_agent(task):
    return f"""
OPERATIONS AGENT RESPONSE:

Task: {task}

Operations checklist:
- Customer name
- Product type
- Quantity
- Price each
- Total
- Due date
- Payment status
- Production status

Suggested next step:
Create order record and mark invoice as SENT.
"""
