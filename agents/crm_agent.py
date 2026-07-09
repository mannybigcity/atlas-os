customers = []

def crm_agent(task):
    return f"""
CRM AGENT RESPONSE:

Task: {task}

CRM action needed:
- Add or update customer
- Track last contact
- Track interested product
- Track next follow-up

Suggested next step:
Save this lead with name, business, phone/email, product interest, and follow-up date.
"""