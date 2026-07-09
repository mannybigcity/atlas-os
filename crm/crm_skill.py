import json
import os
import uuid
from datetime import date, datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROSPECTS_FILE = os.path.join(BASE_DIR, "prospects.json")
CUSTOMERS_FILE = os.path.join(BASE_DIR, "customers.json")

CLOSED_STATUSES = ("closed lost", "lost", "dead", "not now")
WON_STATUSES = ("closed won", "won", "paid", "customer")


def _ensure_file(path, default_value):
    folder = os.path.dirname(os.path.abspath(path))
    if folder:
        os.makedirs(folder, exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default_value, f, indent=2)


def _load_json(path, default_value):
    _ensure_file(path, default_value)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return default_value
    return data if isinstance(data, type(default_value)) else default_value


def _save_json(path, data):
    _ensure_file(path, [] if isinstance(data, list) else {})
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _now_iso():
    return datetime.now().replace(microsecond=0).isoformat()


def _activity_timestamp():
    return datetime.now().isoformat(timespec="microseconds")


def _crm_id():
    return f"crm_{uuid.uuid4().hex[:10]}"


def _activity_id():
    return f"act_{uuid.uuid4().hex[:10]}"


def _money(value):
    if value in (None, ""):
        return 0.0
    try:
        return round(float(str(value).replace("$", "").replace(",", "").strip()), 2)
    except (TypeError, ValueError):
        return 0.0


def _clean_text(value):
    return " ".join(str(value or "").strip().split())


def normalize_activity(activity):
    created_at = activity.get("created_at") or _activity_timestamp()
    return {
        "id": _clean_text(activity.get("id")) or _activity_id(),
        "type": _clean_text(activity.get("type")) or "Note",
        "note": _clean_text(activity.get("note")),
        "next_follow_up": _clean_text(activity.get("next_follow_up")),
        "created_at": created_at,
    }


def _normalized_activities(record):
    activities = record.get("activities", [])
    if not isinstance(activities, list):
        return []
    normalized = [normalize_activity(item) for item in activities if isinstance(item, dict)]
    return sorted(normalized, key=lambda item: item.get("created_at", ""), reverse=True)


def next_action_for_status(status):
    status_text = str(status or "").lower()
    if "invoice" in status_text:
        return "Collect payment and confirm production timeline"
    if "quote" in status_text or "quoted" in status_text:
        return "Follow up on quote and ask for approval"
    if "mockup" in status_text:
        return "Confirm mockup approval and move to invoice"
    if "hot" in status_text:
        return "Send quote / mockup and ask for decision date"
    if any(word in status_text for word in WON_STATUSES):
        return "Deliver order, request review, and ask for referral"
    if any(word in status_text for word in CLOSED_STATUSES):
        return "Archive unless a future opportunity is identified"
    return "Qualify need, budget, and next deadline"


def normalize_prospect(prospect):
    created_at = prospect.get("created_at") or _now_iso()
    status = _clean_text(prospect.get("status")) or "New"
    normalized = {
        "id": _clean_text(prospect.get("id")) or _crm_id(),
        "name": _clean_text(prospect.get("name")),
        "business": _clean_text(prospect.get("business")),
        "product": _clean_text(prospect.get("product")),
        "status": status,
        "value": _money(prospect.get("value")),
        "email": _clean_text(prospect.get("email")),
        "phone": _clean_text(prospect.get("phone")),
        "source": _clean_text(prospect.get("source")),
        "follow_up": _clean_text(prospect.get("follow_up")),
        "notes": _clean_text(prospect.get("notes")),
        "next_action": _clean_text(prospect.get("next_action")) or next_action_for_status(status),
        "activities": _normalized_activities(prospect),
        "created_at": created_at,
        "updated_at": prospect.get("updated_at") or created_at,
    }
    return normalized


def load_prospects():
    prospects = _load_json(PROSPECTS_FILE, [])
    return [normalize_prospect(item) for item in prospects if isinstance(item, dict)]


def save_prospects(prospects):
    _save_json(PROSPECTS_FILE, [normalize_prospect(item) for item in prospects])


def normalize_customer(customer):
    created_at = customer.get("created_at") or _now_iso()
    status = _clean_text(customer.get("status")) or "Active"
    normalized = {
        "id": _clean_text(customer.get("id")) or f"cus_{uuid.uuid4().hex[:10]}",
        "source_prospect_id": _clean_text(customer.get("source_prospect_id")),
        "name": _clean_text(customer.get("name")),
        "business": _clean_text(customer.get("business")),
        "email": _clean_text(customer.get("email")),
        "phone": _clean_text(customer.get("phone")),
        "last_product": _clean_text(customer.get("last_product")),
        "lifetime_value": _money(customer.get("lifetime_value")),
        "status": status,
        "follow_up": _clean_text(customer.get("follow_up")),
        "next_action": _clean_text(customer.get("next_action")) or next_action_for_status(status),
        "notes": _clean_text(customer.get("notes")),
        "activities": _normalized_activities(customer),
        "created_at": created_at,
        "updated_at": customer.get("updated_at") or created_at,
    }
    return normalized


def load_customers():
    customers = _load_json(CUSTOMERS_FILE, [])
    return [normalize_customer(item) for item in customers if isinstance(item, dict)]


def save_customers(customers):
    _save_json(CUSTOMERS_FILE, [normalize_customer(item) for item in customers])


def create_customer(data):
    customer = normalize_customer(data or {})
    if not customer["name"] and not customer["business"]:
        raise ValueError("Customer name or business is required.")

    customer["created_at"] = _now_iso()
    customer["updated_at"] = customer["created_at"]
    customers = load_customers()
    customers.append(customer)
    save_customers(customers)
    return customer


def search_customers(query="", status=""):
    query = str(query or "").strip().lower()
    status = str(status or "").strip().lower()
    customers = load_customers()

    if status:
        customers = [c for c in customers if status in c.get("status", "").lower()]

    if query:
        fields = ("name", "business", "email", "phone", "last_product", "status", "notes", "next_action")
        customers = [
            c for c in customers
            if any(query in str(c.get(field, "")).lower() for field in fields)
        ]

    return sorted(customers, key=lambda c: c.get("updated_at", ""), reverse=True)


def update_customer(identifier, updates):
    customers = load_customers()
    identifier = str(identifier or "").strip().lower()

    for index, customer in enumerate(customers):
        if customer.get("id", "").lower() == identifier or customer.get("name", "").lower() == identifier:
            merged = {**customer, **(updates or {})}
            merged["id"] = customer["id"]
            merged["created_at"] = customer.get("created_at")
            merged["updated_at"] = _now_iso()
            customers[index] = normalize_customer(merged)
            save_customers(customers)
            return customers[index]

    raise ValueError(f"No customer found for {identifier}.")


def delete_customer(identifier):
    customers = load_customers()
    identifier = str(identifier or "").strip().lower()
    kept = [
        customer for customer in customers
        if customer.get("id", "").lower() != identifier and customer.get("name", "").lower() != identifier
    ]
    if len(kept) == len(customers):
        raise ValueError(f"No customer found for {identifier}.")
    save_customers(kept)
    return True


def _add_touchpoint_to_records(records, identifier, updates, record_label):
    identifier = str(identifier or "").strip().lower()
    touchpoint = normalize_activity(updates or {})
    if not touchpoint["note"]:
        raise ValueError("Touchpoint note is required.")

    for index, record in enumerate(records):
        if record.get("id", "").lower() == identifier or record.get("name", "").lower() == identifier:
            activities = [touchpoint] + record.get("activities", [])
            merged = {**record, "activities": activities, "updated_at": _now_iso()}
            if touchpoint.get("next_follow_up"):
                merged["follow_up"] = touchpoint["next_follow_up"]
            records[index] = merged
            return touchpoint, records

    raise ValueError(f"No {record_label} found for {identifier}.")


def add_prospect_touchpoint(identifier, data):
    prospects = load_prospects()
    touchpoint, prospects = _add_touchpoint_to_records(prospects, identifier, data, "prospect")
    save_prospects(prospects)
    return touchpoint


def add_customer_touchpoint(identifier, data):
    customers = load_customers()
    touchpoint, customers = _add_touchpoint_to_records(customers, identifier, data, "customer")
    save_customers(customers)
    return touchpoint


def get_activity_timeline(limit=25):
    timeline = []
    for prospect in load_prospects():
        for activity in prospect.get("activities", []):
            timeline.append({
                **activity,
                "record_type": "prospect",
                "record_id": prospect.get("id", ""),
                "record_name": prospect.get("name", ""),
                "business": prospect.get("business", ""),
            })
    for customer in load_customers():
        for activity in customer.get("activities", []):
            timeline.append({
                **activity,
                "record_type": "customer",
                "record_id": customer.get("id", ""),
                "record_name": customer.get("name", ""),
                "business": customer.get("business", ""),
            })

    timeline.sort(key=lambda item: item.get("created_at", ""), reverse=True)
    try:
        limit = max(1, int(limit))
    except (TypeError, ValueError):
        limit = 25
    return timeline[:limit]


def create_prospect(data):
    prospect = normalize_prospect(data or {})
    if not prospect["name"] and not prospect["business"]:
        raise ValueError("Prospect name or business is required.")

    prospect["created_at"] = _now_iso()
    prospect["updated_at"] = prospect["created_at"]
    prospect["next_action"] = next_action_for_status(prospect["status"])

    prospects = load_prospects()
    prospects.append(prospect)
    save_prospects(prospects)
    return prospect


def add_prospect(name, business, product, status, notes=""):
    prospect = create_prospect({
        "name": name,
        "business": business,
        "product": product,
        "status": status,
        "notes": notes,
    })
    return f"Prospect added: {prospect['name']} - {prospect['business']} - {prospect['product']} - {prospect['status']}"


def find_prospect(identifier):
    identifier = str(identifier or "").strip().lower()
    for prospect in load_prospects():
        if prospect.get("id", "").lower() == identifier:
            return prospect
        if prospect.get("name", "").lower() == identifier:
            return prospect
        if prospect.get("business", "").lower() == identifier:
            return prospect
    return None


def update_prospect(identifier, updates):
    prospects = load_prospects()
    identifier = str(identifier or "").strip().lower()

    for index, prospect in enumerate(prospects):
        if prospect.get("id", "").lower() == identifier or prospect.get("name", "").lower() == identifier:
            merged = {**prospect, **(updates or {})}
            merged["id"] = prospect["id"]
            merged["created_at"] = prospect.get("created_at")
            merged["updated_at"] = _now_iso()
            if "status" in (updates or {}) and "next_action" not in (updates or {}):
                merged["next_action"] = next_action_for_status(merged.get("status"))
            prospects[index] = normalize_prospect(merged)
            save_prospects(prospects)
            return prospects[index]

    raise ValueError(f"No prospect found for {identifier}.")


def update_prospect_status(name, new_status):
    try:
        update_prospect(name, {"status": new_status})
    except ValueError:
        return f"No prospect found named {name}."
    return f"Updated {name} to status: {new_status}"


def delete_prospect(identifier):
    prospects = load_prospects()
    identifier = str(identifier or "").strip().lower()
    kept = [
        prospect for prospect in prospects
        if prospect.get("id", "").lower() != identifier and prospect.get("name", "").lower() != identifier
    ]
    if len(kept) == len(prospects):
        raise ValueError(f"No prospect found for {identifier}.")
    save_prospects(kept)
    return True


def search_prospects(query="", status=""):
    query = str(query or "").strip().lower()
    status = str(status or "").strip().lower()
    prospects = load_prospects()

    if status:
        prospects = [p for p in prospects if status in p.get("status", "").lower()]

    if query:
        fields = ("name", "business", "product", "status", "notes", "email", "phone", "source")
        prospects = [
            p for p in prospects
            if any(query in str(p.get(field, "")).lower() for field in fields)
        ]

    return sorted(prospects, key=lambda p: (p.get("follow_up") or "9999-12-31", -p.get("value", 0)))


def _parse_date(value):
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def _is_active_pipeline(prospect):
    status = prospect.get("status", "").lower()
    if any(word in status for word in CLOSED_STATUSES):
        return False
    if any(word in status for word in WON_STATUSES):
        return False
    return True


def get_crm_dashboard():
    prospects = load_prospects()
    customers = load_customers()
    today = date.today()
    active = [p for p in prospects if _is_active_pipeline(p)]
    followups = [item for item in prospects + customers if item.get("follow_up")]
    overdue = 0
    due_today = 0
    upcoming = 0

    for item in followups:
        follow_up_date = _parse_date(item.get("follow_up"))
        if follow_up_date is None or follow_up_date > today:
            upcoming += 1
        elif follow_up_date == today:
            due_today += 1
        else:
            overdue += 1

    by_status = {}
    for prospect in prospects:
        status = prospect.get("status") or "New"
        by_status[status] = by_status.get(status, 0) + 1

    next_money_target = None
    if active:
        next_money_target = max(active, key=lambda p: p.get("value", 0))

    active_customers = [c for c in customers if "inactive" not in c.get("status", "").lower()]
    customer_lifetime_value = round(sum(c.get("lifetime_value", 0) for c in customers), 2)

    return {
        "total_prospects": len(prospects),
        "active_prospects": len(active),
        "active_pipeline_value": round(sum(p.get("value", 0) for p in active), 2),
        "closed_won": len([p for p in prospects if any(word in p.get("status", "").lower() for word in WON_STATUSES)]),
        "closed_lost": len([p for p in prospects if any(word in p.get("status", "").lower() for word in CLOSED_STATUSES)]),
        "followups_total": len(followups),
        "followups_due_today": due_today,
        "followups_overdue": overdue,
        "followups_upcoming": upcoming,
        "total_customers": len(customers),
        "active_customers": len(active_customers),
        "customer_lifetime_value": customer_lifetime_value,
        "by_status": by_status,
        "next_money_target": next_money_target,
        "prospects": search_prospects(),
        "customers": search_customers(),
    }


def get_followups():
    followups = []
    for prospect in load_prospects():
        if prospect.get("follow_up"):
            followups.append({**prospect, "record_type": "prospect"})
    for customer in load_customers():
        if customer.get("follow_up"):
            followups.append({**customer, "record_type": "customer"})
    return sorted(followups, key=lambda item: item.get("follow_up") or "9999-12-31")


def convert_prospect_to_customer(identifier):
    prospect = find_prospect(identifier)
    if not prospect:
        raise ValueError(f"No prospect found for {identifier}.")

    customers = load_customers()
    existing = None
    for customer in customers:
        if customer.get("source_prospect_id") == prospect["id"]:
            existing = customer
            break

    customer_data = {
        "id": existing.get("id") if existing else f"cus_{uuid.uuid4().hex[:10]}",
        "source_prospect_id": prospect["id"],
        "name": prospect.get("name", ""),
        "business": prospect.get("business", ""),
        "email": prospect.get("email", ""),
        "phone": prospect.get("phone", ""),
        "last_product": prospect.get("product", ""),
        "lifetime_value": _money(prospect.get("value")),
        "notes": prospect.get("notes", ""),
        "created_at": existing.get("created_at") if existing else _now_iso(),
        "updated_at": _now_iso(),
    }

    if existing:
        customers = [customer_data if c.get("id") == existing.get("id") else c for c in customers]
    else:
        customers.append(customer_data)
    save_customers(customers)
    return customer_data


def get_prospect_summary():
    prospects = load_prospects()

    total = len(prospects)
    hot = 0
    quoted = 0
    invoice_sent = 0
    won = 0
    lost = 0

    for p in prospects:
        status = str(p.get("status", "")).lower()

        if "hot" in status:
            hot += 1
        elif "quote" in status:
            quoted += 1
        elif "invoice" in status:
            invoice_sent += 1
        elif "won" in status or "paid" in status:
            won += 1
        elif "lost" in status:
            lost += 1

    return {
        "total": total,
        "hot": hot,
        "quoted": quoted,
        "invoice_sent": invoice_sent,
        "won": won,
        "lost": lost,
        "prospects": prospects
    }


def show_prospects():
    summary = get_prospect_summary()

    if summary["total"] == 0:
        return "No prospects saved yet."

    lines = []

    lines.append("PROSPECT COMMAND CENTER")
    lines.append("")
    lines.append(f"Total Prospects: {summary['total']}")
    lines.append(f"Hot Prospects: {summary['hot']}")
    lines.append(f"Quotes Sent: {summary['quoted']}")
    lines.append(f"Invoices Sent: {summary['invoice_sent']}")
    lines.append(f"Closed Won: {summary['won']}")
    lines.append(f"Closed Lost: {summary['lost']}")
    lines.append("")
    lines.append("PROSPECT LIST:")

    for p in summary["prospects"]:
        line = f"{p.get('name', '')} | {p.get('business', '')} | {p.get('product', '')} | {p.get('status', '')}"
        if p.get("value"):
            line += f" | ${p.get('value'):,.2f}"
        if p.get("follow_up"):
            line += f" | Follow up: {p.get('follow_up')}"
        if p.get("notes"):
            line += f" | Notes: {p.get('notes')}"
        lines.append(line)

    return "\n".join(lines)
