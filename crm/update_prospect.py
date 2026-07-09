from crm.crm_skill import load_prospects, save_prospects

def update_prospect_status(name, new_status):
    prospects = load_prospects()

    for prospect in prospects:
        if prospect["name"].lower() == name.lower():
            prospect["status"] = new_status
            save_prospects(prospects)
            return f"Updated {name} to status: {new_status}"

    return f"No prospect found named {name}."